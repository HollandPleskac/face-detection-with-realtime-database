import cv2
import os

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
print(imgModeList)

while cap.isOpened():
  success, img = cap.read()

  # Overlay webcam on graphics
  imgBackground[162:162+480, 55:55+640] = img # starting height: ending height, starting width: ending width
  imgBackground[44:44+633, 808:808+414] = imgModeList[0]


  cv2.imshow("Face Attendance",imgBackground)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()

