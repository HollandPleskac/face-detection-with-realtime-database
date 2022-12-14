import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720) # graphics based on these dimensions

while cap.isOpened():
  success, img = cap.read()
  cv2.imshow("Face Attendance", img)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()

