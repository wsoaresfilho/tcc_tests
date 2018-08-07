import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('quadro.jpeg')
img_sift  = img.copy()
img_surf  = img.copy()
img_fast  = img.copy()
img_orb   = img.copy()
img_brisk = img.copy()

def sift_thread():
	sift = cv2.xfeatures2d.SIFT_create()
	(kps, descs) = sift.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray, kps, img_sift, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#cv2.imshow('SIFT Algorithm', img_sift)


def surf_thread():
	surf = cv2.xfeatures2d.SURF_create()
	(kps2, descs2) = surf.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray, kps2, img_surf, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#cv2.imshow('SURF Algorithm', img_surf)

def fast_thread():
	fast = cv2.FastFeatureDetector_create()
	kps3 = fast.detect(gray, None)
	cv2.drawKeypoints(gray, kps3, img_fast, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#cv2.imshow('FAST Algorithm', img_fast)

def orb_thread():
	orb = cv2.ORB_create()
	kps4 = orb.detect(gray, None)
	(kps4, des4) = orb.compute(gray, kps4)
	cv2.drawKeypoints(gray, kps4, img_orb, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#cv2.imshow('ORB Algorithm', img_orb)

def brisk_thread():
	brisk = cv2.BRISK_create()
	(kps5, descs5) = brisk.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray, kps5, img_brisk, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#cv2.imshow('BRISK Algorithm', img_brisk)


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
sift_thread()
surf_thread()
fast_thread()
orb_thread()
brisk_thread()

output = np.hstack([img_sift, img_surf, img_orb, img_brisk])
cv2.namedWindow('SIFT vs SURF vs ORB vs BRISK', cv2.WINDOW_NORMAL)
cv2.imshow('SIFT vs SURF vs ORB vs BRISK', output)
#cv2.resizeWindow('SIFT vs SURF vs ORB vs BRISK', 600,600)

k = cv2.waitKey(0) & 0xFF

if k == 27:         # wait for ESC key to exit
  cv2.destroyAllWindows()
else:
  print("Exit")