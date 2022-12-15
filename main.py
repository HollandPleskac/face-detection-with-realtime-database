import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

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
  imgBackground[44:44+633, 808:808+414] = imgModeList[0]

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


  cv2.imshow("Face Attendance",imgBackground)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()

