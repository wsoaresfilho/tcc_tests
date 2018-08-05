import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('quadro.jpeg')
img2 = img
img3 = img
img4 = img

def sift_thread():
	sift = cv2.xfeatures2d.SIFT_create()
	(kps, descs) = sift.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray, kps, img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	cv2.imshow('SIFT Algorithm', img)


def surf_thread():
	surf = cv2.xfeatures2d.SURF_create()
	(kps2, descs2) = surf.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray, kps2, img2, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	cv2.imshow('SURF Algorithm', img2)

def fast_thread():
	fast = cv2.FastFeatureDetector_create()
	kps3 = fast.detect(gray, None)
	cv2.drawKeypoints(gray, kps3, img3, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	cv2.imshow('FAST Algorithm', img3)

def orb_thread():
	orb = cv2.ORB_create()
	kps4 = orb.detect(gray, None)
	(kps4, des4) = orb.compute(gray, kps4)
	cv2.drawKeypoints(gray, kps4, img4, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	cv2.imshow('ORB Algorithm', img4)


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
sift_thread()
surf_thread()
fast_thread()
orb_thread()

k = cv2.waitKey(0) & 0xFF

if k == 27:         # wait for ESC key to exit
  cv2.destroyAllWindows()
else:
  print("Exit")