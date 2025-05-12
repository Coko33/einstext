import cv2

img = cv2.imread("./frames/hablaEin00.jpg")
cv2.imshow("Test", img)

while True:
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()