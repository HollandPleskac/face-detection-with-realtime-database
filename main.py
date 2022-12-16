import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to DB
DATABASE_URL = os.getenv('DATABASE_URL')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')
print("DB URL", DATABASE_URL)
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL,
    'storageBucket': STORAGE_BUCKET
})

bucket = storage.bucket()


cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480) # graphics based on these dimensions

imgBackground = cv2.imread("resources/background.png")

# Import mode images into a list (imgModeList)
# imgModeList literally contains images (represented as array of rgb pixels)
folderModePath = "resources/modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
  imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(imgModeList)

# Load Encoding File
print("Loading Encode File...")
file = open("EncodeFile.p", "rb")
encodingsListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodingsListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
frameCounter = 0 # only download in first frame!
id = -1
imgStudent = []

while cap.isOpened():
  success, img = cap.read()

  # Scale down image to 1/4th original to reduce computational power
  imgSmall = cv2.resize(img,(0,0),None,0.25,0.25)
  imgSmallRGB = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

  # Get location of face in current frame
  faceCurrentFame = face_recognition.face_locations(imgSmall)
  # Find encodings of face in current frame
  encodeCurrentFrame = face_recognition.face_encodings(imgSmall, faceCurrentFame)

  # Overlay webcam on graphics
  imgBackground[162:162+480, 55:55+640] = img # starting height: ending height, starting width: ending width
  imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

  # Compare face in frame to encodings of known faces
  for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFame):
    matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
    faceDistance = face_recognition.face_distance(encodeListKnown,encodeFace)
    # print("matches", matches)
    # print("face distance", faceDistance)

    # Want lowest known face's distance from face in frame
    matchIndex = np.argmin(faceDistance)
    # print("match index", matchIndex)

    # matches can all be false if an unknown face is in frame
    if matches[matchIndex] == True:
      # print("Known face detected")
      # print(studentIds[matchIndex])
      # Draw bounding box around face
      y1, x2, y2, x1 = faceLocation
      y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4 # *4 because we reduced image to 1/4
      bbox = 55+x1, 162+y1, x2-x1, y2-y1 # 55 and 162 are offsets because of the backgroundImage
      imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=1) # bbox = bounding box, rt = rectangle thickness
      id = studentIds[matchIndex]

      if frameCounter == 0:
        frameCounter = 1
        modeType = 1 # face detected, change screen mode
  
  if frameCounter != 0:

    # Download data from database only on first frame with face!
    if frameCounter == 1:
      studentInfo = db.reference(f'Students/{id}').get()
      print("Student Info Downloaded:",studentInfo)
      # Get the Image from the storage
      blob = bucket.get_blob(f'images\{id}.jpg')
      array = np.frombuffer(blob.download_as_string(),np.uint8)
      imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
      # Update data of attendance
      ref = db.reference(f'Students/{id}')
      studentInfo['total_attendance'] += 1 # update locally
      # update in db
      ref.child('total_attendance').set(studentInfo['total_attendance'])


    # Display database information onto the window
    cv2.putText(imgBackground, str(studentInfo['total_attendance']),(861,125),
                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
    cv2.putText(imgBackground, str(studentInfo['major']),(1006,550),
                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
    cv2.putText(imgBackground, str(id),(1006,493),
                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
    cv2.putText(imgBackground, str(studentInfo['standing']),(910,625),
                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
    cv2.putText(imgBackground, str(studentInfo['year']),(1025,625),
                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
    cv2.putText(imgBackground, str(studentInfo['starting_year']),(1125,625),
                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
    
    # Center Name
    (width,height), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
    offset = (414-width)//2 # 414 is width of section of img
    cv2.putText(imgBackground, str(studentInfo['name']),(808+offset,445),
                cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

    # put in image of student
    # My Images are 700x700 and the shape of images accepted by the ui is 216 by 216.  So I will just not display the images
    # The focus of this project isn't to spend too much time resizing images anyways
    # imgBackground[175:175+216,909:909+216] = imgStudent # 216 is width and height of image

    frameCounter+=1



  cv2.imshow("Face Attendance",imgBackground)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()

