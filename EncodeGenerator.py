# Import Faces
# Encode Faces
# Store encoded faces in list
# Dump using pickle

import cv2
import face_recognition
import pickle
import os

# Import student images
folderModePath = "images"
pathList = os.listdir(folderModePath)
imgList = []
studentIds = []
for path in pathList:
  imgList.append(cv2.imread(os.path.join(folderModePath, path)))
  # get name of image which is the id
  id = os.path.splitext(path)[0]
  studentIds.append(id)
print(studentIds)


def findEncodings(imagesList):
  encodingsList = []
  for img in imagesList:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    encodingsList.append(encode)

  return encodingsList

print("Encoding Started...")
encodingsListKnown = findEncodings(imgList)
encodingsListKnownWithIds = [encodingsListKnown, studentIds]
print(encodingsListKnown)
print("Encoding Complete")

file = open("EncodeFile.p","wb")
pickle.dump(encodingsListKnownWithIds, file)
file.close()
print("File Saved")


