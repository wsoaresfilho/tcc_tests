# -*- coding: utf-8 -*-

import cv2 as cv
import numpy as np
import threading
import pyttsx3 as tts
#Differents logging levels are available : trace, debug, info, warning, error and critical.
from kivy.logger import Logger

# Constants of configuration
FLANN_INDEX_KDITREE=2
VIDEO_WIDTH=960.0
VIDEO_HEIGHT=540.0
#ALGO_TYPE=3 # SIFT=0 , SURF=1 , ORB=2, BRISK=3, KAZE=4, AKAZE=5

# Informações que devem ser cadastradas e salvas em BD
list_threads=[]

# Inicialização do áudio
speaker = tts.init()

# Função para "falar" o nome do objeto via áudio
def play_audio(name):
    speaker.say(name)
    speaker.runAndWait()
    list_threads = []

def getClosestPoint(obj, center):
    closest = []
    for i, corner in enumerate(obj):
        x = corner[0]-center[0]
        y = corner[1]-center[1]
        total = abs(x) + abs(y)
        closest.append(total)

    return min(closest)


def getDetection(videoimg, config):
    detector, flann = config.detector
    minMatches = int(config.minMatches.text)
    match_distance = float(config.distance.text)

    camImgBGR = videoimg
    camImgGray = cv.cvtColor(camImgBGR, cv.COLOR_BGR2GRAY)
    queryKP, queryDesc = detector.detectAndCompute(camImgGray,None)
    closest_points = []
    detected_obj_qty=0
    
    # Percorre os objetos e os seus descritores
    for obj_index, item_obj in enumerate(config.list_objects):
        closest_points.append(None)
        if(len(list_threads) < len(config.list_objects)):
            list_threads.append(None)

        for obj_desc_index, obj_descriptor in enumerate(item_obj.trainDescs):
            goodMatch = []
            matches = flann.knnMatch(queryDesc, obj_descriptor, k=2)

            for m, n in matches:
                if(m.distance < (match_distance * n.distance)):
                    goodMatch.append(m)
    
            if(len(goodMatch) > minMatches):
                detected_obj_qty = detected_obj_qty + 1
                obj_points = []
                video_points = []
                for m in goodMatch:
                    obj_points.append(item_obj.trainKPs[obj_desc_index][m.trainIdx].pt)
                    video_points.append(queryKP[m.queryIdx].pt)
                obj_points, video_points = np.float32((obj_points,video_points))
                homog, _ = cv.findHomography(obj_points, video_points,cv.RANSAC, 3.0)
                obj_height, obj_width = item_obj.trainImgs[obj_desc_index].shape
                trainBorder = np.float32([[ [0,0], [0,obj_height-1], [obj_width-1,obj_height-1], [obj_width-1,0] ]])
                queryBorder = cv.perspectiveTransform(trainBorder, homog)
                corners = np.int32(queryBorder)
                # Pega o ponto mais próximo do centro do vídeo
                closest_points[obj_index] = getClosestPoint(corners[0], [VIDEO_WIDTH/2, VIDEO_HEIGHT/2])

                # Desenha o quadrado ao redor do objeto
                cv.polylines(camImgBGR, [np.int32(queryBorder)], True, item_obj.color, 3)
                # Escreve o texto do objeto
                cv.putText(camImgBGR, item_obj.name, (corners[0][0][0], corners[0][0][1]-10), 2, 1, item_obj.color, 2)

                # Aplica o áudio apenas se nao tiver um áudio em andamento
                if(config.playAudio):
                    t = threading.Thread(target=play_audio, args=(item_obj.name,))
                    list_threads[obj_index] = t

                Logger.info('Detection: Found object %d => Image num: %d - %s' %(obj_index + 1, obj_desc_index + 1, item_obj.name))
                # Sai do loop pois ja achou o objeto
                break
            else:
                Logger.info('Detection: Not Enough match found for object %d - %d/%d' %(obj_index + 1, len(goodMatch), minMatches))
                
    
    # Retorna o mais proximo do centro dos objetos que foram reconhecidos
    filtered_points = filter(lambda a: a != None, closest_points)
    if(filtered_points):
        min_point = min(filtered_points)
        index = closest_points.index(min_point)
        if(config.playAudio and len(threading.enumerate()) == 1):
            list_threads[index].start()

    if(config.showCenterCircles):
        videoHeight, videoWidth, channels = camImgBGR.shape
        #print "Video: Width: %d, Height: %d"%(videoWidth, videoHeight)
        cv.circle(camImgBGR, (videoWidth/2, videoHeight/2), int(videoHeight/2.5), (0,180,255), 1)
        cv.circle(camImgBGR, (videoWidth/2, videoHeight/2), int(videoHeight/10), (0,0,255), 2)


    return (camImgBGR, detected_obj_qty)

