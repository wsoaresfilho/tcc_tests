# -*- coding: utf-8 -*-

import cv2 as cv
import numpy as np
import threading
import pyttsx3 as tts
# Differents logging levels are available : trace, debug, info, warning, error and critical.
from kivy.logger import Logger


# Array to hold and control the audio threads
audio_threads=[]

# Initialize the TTS audio lib
speaker = tts.init()
speaker.setProperty('voice', 'english-us') # uses an american voice
#speaker.setProperty('voice', 'brazil') # uses a brazilian voice

# Functions that plays/speaks the obj name (audio)
def play_audio(name):
    speaker.say(name)
    speaker.runAndWait()
    audio_threads = []

# Function that returns the point closest to the center
def getClosestPoint(obj, center):
    closest = []
    for i, corner in enumerate(obj):
        x = corner[0]-center[0]
        y = corner[1]-center[1]
        total = abs(x) + abs(y)
        closest.append(total)

    return min(closest)

# Function that does the real object detection
def getDetection(videoimg, config):
    # Gets parameters from configuration
    # get the detector and the matcher
    detector, matcher = config.detector
    # get the minimun number of keypoint matches to say a detection occurred
    minMatches = int(config.minMatches.text)
    # the proportional distance to define a good match
    match_distance = float(config.distance.text)

    # Get the video img (BGR and grayscale)
    cameraImgBGR = videoimg
    cameraImgGray = cv.cvtColor(cameraImgBGR, cv.COLOR_BGR2GRAY)
    # Get the keypoints and the descriptors of the video img
    videoKeyPoints, videoDescriptors = detector.detectAndCompute(cameraImgGray, None)
    # Array to save the points closest to the center
    closest_points = []
    # Variable to get the number of objects detected
    detected_obj_qty = 0
    
    # Iterates through the objects registered in the app
    for obj_index, item_obj in enumerate(config.list_objects):
        # Reset the array of closest points
        closest_points.append(None)
        
        if(len(audio_threads) < len(config.list_objects)):
            audio_threads.append(None)

        # Iterates through the object descriptors
        for obj_desc_index, obj_descriptor in enumerate(item_obj.objDescriptors):
            # Array of good matches
            goodMatch = []
            # Get all the matches between video and obj using knn matching
            matches = matcher.knnMatch(videoDescriptors, obj_descriptor, k=2)

            # Iterates through the matches to get the "good" ones based on the distance
            for m, n in matches:
                if(m.distance < (match_distance * n.distance)):
                    goodMatch.append(m)
    
            # If there are more good matches than the minimum defined in config
            if(len(goodMatch) > minMatches):
                detected_obj_qty = detected_obj_qty + 1
                obj_points = []
                video_points = []

                # Get only the good points in obj and video
                for m in goodMatch:
                    obj_points.append(item_obj.objKeyPoints[obj_desc_index][m.trainIdx].pt)
                    video_points.append(videoKeyPoints[m.queryIdx].pt)
                
                obj_points, video_points = np.float32((obj_points,video_points))
                homog, _ = cv.findHomography(obj_points, video_points, cv.RANSAC, 3.0)
                # Get the obj height and width
                obj_height, obj_width = item_obj.objImages[obj_desc_index].shape
                # Get the borders and corners
                objBorder = np.float32([[ [0,0], [0,obj_height-1], [obj_width-1,obj_height-1], [obj_width-1,0] ]])
                videoBorder = cv.perspectiveTransform(objBorder, homog)
                corners = np.int32(videoBorder)
                # Gets the closest points to the center
                closest_points[obj_index] = getClosestPoint(corners[0], [config.video_width/2, config.video_height/2])

                # Draws a square around the detected obj
                cv.polylines(cameraImgBGR, [np.int32(videoBorder)], True, item_obj.color, 3)
                # Writes the detected obj name above the square
                cv.putText(cameraImgBGR, item_obj.name, (corners[0][0][0], corners[0][0][1]-10), 2, 1, item_obj.color, 2)

                # If audio config is set
                if(config.playAudio):
                    # only plays the audio if there is no audio already playing
                    t = threading.Thread(target=play_audio, args=(item_obj.name,))
                    audio_threads[obj_index] = t

                Logger.info('Detection: Found object %d => Image num: %d - %s' %(obj_index + 1, obj_desc_index + 1, item_obj.name))
                # If an obj was already found there is no need to look for the same obj again, so break the loop
                break
            else:
                Logger.info('Detection: Not Enough match found for object %d - %d/%d' %(obj_index + 1, len(goodMatch), minMatches))
                
    
    # If there is more than one obj detected, speaks the name of the closest to the center
    filtered_points = filter(lambda a: a != None, closest_points)
    if(filtered_points):
        min_point = min(filtered_points)
        index = closest_points.index(min_point)
        if(config.playAudio and len(threading.enumerate()) == 1):
            audio_threads[index].start()

    # Shows center colored circles if the config is set
    if(config.showCenterCircles):
        videoHeight, videoWidth, channels = cameraImgBGR.shape
        #print "Video: Width: %d, Height: %d"%(videoWidth, videoHeight)
        cv.circle(cameraImgBGR, (videoWidth/2, videoHeight/2), int(videoHeight/2.5), (0,180,255), 1)
        cv.circle(cameraImgBGR, (videoWidth/2, videoHeight/2), int(videoHeight/10), (0,0,255), 2)

    # Returns the video frame with detection and the number of objects detected
    return (cameraImgBGR, detected_obj_qty)

