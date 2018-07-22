import numpy as np
import cv2 as cv

# Load an color image in grayscale
img = cv.imread('elisa.jpg',0)

cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.imshow('image',img)
k = cv.waitKey(0) & 0xFF

if k == 27:         # wait for ESC key to exit
  cv.destroyAllWindows()
elif k == ord('s'): # wait for 's' key to save and exit
  cv.imwrite('teste.png',img)
  cv.destroyAllWindows()
else:
  print("Exit")