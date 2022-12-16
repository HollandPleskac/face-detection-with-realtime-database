# Import Faces
# Encode Faces
# Store encoded faces in list
# Dump using pickle

import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')
print("DB URL", DATABASE_URL)
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL,
    'storageBucket': STORAGE_BUCKET
})

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

  # Add Images to Firebase
  fileName = os.path.join(folderModePath,path)
  bucket = storage.bucket()
  blob = bucket.blob(fileName)
  blob.upload_from_filename(fileName)

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


