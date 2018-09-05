import numpy as np
import cv2
from scipy.signal import savgol_filter

SMOOTH_CONTOUR = True

def getSobel (channel):
    sobelx = cv2.Sobel(channel, cv2.CV_16S, 1, 0, borderType=cv2.BORDER_REPLICATE)
    sobely = cv2.Sobel(channel, cv2.CV_16S, 0, 1, borderType=cv2.BORDER_REPLICATE)
    sobel = np.hypot(sobelx, sobely)
    return sobel

def findSignificantContours (img, sobel_8u):
    image, contours, heirarchy = cv2.findContours(sobel_8u, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find level 1 contours
    level1 = []
    for i, tupl in enumerate(heirarchy[0]):
        # Each array is in format (Next, Prev, First child, Parent)
        # Filter the ones without parent
        if tupl[3] == -1:
            tupl = np.insert(tupl, 0, [i])
            level1.append(tupl)

    # From among them, find the contours with large surface area.
    significant = []
    tooSmall = sobel_8u.size * 5 / 100 # If contour isn't covering 5% of total area of image then it probably is too small
    for tupl in level1:
        contour = contours[tupl[0]]

        ## Use Savitzky-Golay filter to smoothen contour.
        if(SMOOTH_CONTOUR):
          window_size = int(round(min(img.shape[0], img.shape[1]) * 0.05)) # Consider each window to be 5% of image dimensions
          savgol_mode = 'mirror' # mirror, constant, wrap, nearest
          x = savgol_filter(contour[:,0,0], window_size * 2 + 1, 3, mode=savgol_mode)
          y = savgol_filter(contour[:,0,1], window_size * 2 + 1, 3, mode=savgol_mode)
          approx = np.empty((x.size, 1, 2))
          approx[:,0,0] = x
          approx[:,0,1] = y
          approx = approx.astype(int)
          contour = approx

        area = cv2.contourArea(contour)
        if area > tooSmall:
            #cv2.drawContours(img, [contour], 0, (0,255,0),2, cv2.LINE_AA, maxLevel=1)
            significant.append([contour, area])

    significant.sort(key=lambda x: x[1])
    return [x[0] for x in significant];

def segment(img):
    blurred = cv2.GaussianBlur(img, (5, 5), 0) # Remove noise

    # Edge operator
    sobel = np.max( np.array([ getSobel(blurred[:,:, 0]), getSobel(blurred[:,:, 1]), getSobel(blurred[:,:, 2]) ]), axis=0 )

    # Noise reduction
    mean = np.mean(sobel)

    # Zero any values less than mean. This reduces a lot of noise.
    sobel[sobel <= mean] = 0
    sobel[sobel > 255] = 255

    #cv2.imwrite('sobel.png', sobel);

    sobel_8u = np.asarray(sobel, np.uint8)

    # Find contours
    significant = findSignificantContours(img, sobel_8u)

    # Mask
    mask = sobel.copy()
    mask[mask > 0] = 0
    cv2.fillPoly(mask, significant, 255)
    # Invert mask
    mask = np.logical_not(mask)

    #Finally remove the background
    img[mask] = 0
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(img)
    rgba = [b,g,r, alpha]
    final_img = cv2.merge(rgba,4)

    return final_img

    # Save the new image with the object and a transparent background
    #cv2.imwrite('..\imgsamples\obj_new.png', final_img);

    # Show the new image
    #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    #cv2.imshow('image', final_img)
    #cv2.resizeWindow('image', 600,600)
    #cv2.waitKey()
