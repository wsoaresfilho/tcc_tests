import cv2 as cv
import numpy as np
from objeto import Objeto

# Constants of configuration
MIN_MATCH_COUNT=22
SIMULATE_REAL_DEVICE=False
FLANN_INDEX_KDITREE=2
FLANN_INDEX_LSH=6
VIDEO_WIDTH=960.0
VIDEO_HEIGHT=540.0
MATCH_DISTANCE=0.75
ALGO_TYPE=3 # SIFT=0 , SURF=1 , ORB=2, BRISK=3

# Informacoes que devem ser cadastradas e salvas em BD
objetos=[]
images=[["unizinco.jpg", "unizinco2.jpg", "unizinco3.jpg"], ["rinosoro.jpg"]]
img_names=["unizinco", "rinosoro"]
#images=[["calculadora.png"]]
#img_names=["calculadora"]

# Inicializacao da camera
cam=cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)

if(ALGO_TYPE == 0):
    detector=cv.xfeatures2d.SIFT_create()
elif(ALGO_TYPE == 1):
    detector=cv.xfeatures2d.SURF_create()
elif(ALGO_TYPE == 2):
    detector=cv.ORB_create(nfeatures=1000, scaleFactor = 1.2, WTA_K = 2, scoreType=cv.ORB_FAST_SCORE)
elif(ALGO_TYPE == 3):
    detector=cv.BRISK_create()

if(ALGO_TYPE == 0 or ALGO_TYPE == 1):
    flannParam=dict(algorithm=FLANN_INDEX_KDITREE,tree=5)
    flann=cv.FlannBasedMatcher(flannParam,{})
elif(ALGO_TYPE == 2 or ALGO_TYPE == 3):
    flann=cv.BFMatcher(cv.NORM_HAMMING)
    #flannParam= dict(algorithm = FLANN_INDEX_LSH,
    #                table_number = 12, # 12
    #                key_size = 20, # 20
    #                multi_probe_level = 2) #2
    #search_params = dict(checks=20)
    #flann=cv.FlannBasedMatcher(flannParam,search_params)

# Criacao dos objetos
for index,imageArray in enumerate(images):
    objetos.append(Objeto(img_names[index], imageArray, detector))


while True:
    ret, QueryImgBGR=cam.read()
    QueryImg=cv.cvtColor(QueryImgBGR,cv.COLOR_BGR2GRAY)
    queryKP,queryDesc=detector.detectAndCompute(QueryImg,None)
    
    # Percorre os objetos e os seus descritores
    for obj_index, objeto in enumerate(objetos):
        for obj_desc_index, obj_descriptor in enumerate(objeto.trainDescs):
            goodMatch=[]
            matches=flann.knnMatch(queryDesc, obj_descriptor, k=2)

            for m, n in matches:
                if(m.distance < (MATCH_DISTANCE * n.distance)):
                    goodMatch.append(m)
    
            if(len(goodMatch) > MIN_MATCH_COUNT):
                obj_points=[]
                video_points=[]
                for m in goodMatch:
                    obj_points.append(objeto.trainKPs[obj_desc_index][m.trainIdx].pt)
                    video_points.append(queryKP[m.queryIdx].pt)
                obj_points, video_points = np.float32((obj_points,video_points))
                homog, _ = cv.findHomography(obj_points, video_points,cv.RANSAC, 3.0)
                obj_height, obj_width = objeto.trainImgs[obj_desc_index].shape
                trainBorder = np.float32([[ [0,0], [0,obj_height-1], [obj_width-1,obj_height-1], [obj_width-1,0] ]])
                queryBorder = cv.perspectiveTransform(trainBorder, homog)
                corners=np.int32(queryBorder)
                # Desenha o quadrado ao redor do objeto
                cv.polylines(QueryImgBGR, [np.int32(queryBorder)], True, objeto.color, 3)
                # Escreve o texto do objeto
                cv.putText(QueryImgBGR, objeto.name, (corners[0][0][0], corners[0][0][1]-10), 2, 1, objeto.color, 2)

                print "Found object %d => Image num: %d - %s"%(obj_index+1, obj_desc_index+1, images[obj_index][obj_desc_index])
                # Break for loop because already found the object
                break
            else:
                print "Not Enough match found for object %d - %d/%d"%(obj_index+1, len(goodMatch), MIN_MATCH_COUNT)

    if SIMULATE_REAL_DEVICE:
        videoWidth = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
        videoHeight = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))
        #print "Video: Width: %d, Height: %d"%(videoWidth, videoHeight)
        cv.circle(QueryImgBGR,(videoWidth/2,videoHeight/2), videoHeight/3, (0,0,255), 1)

    # Abre a janela com o video
    cv.imshow('Reconhecimento de Objetos', QueryImgBGR)

    # Para sair pressione a tecla "q"
    if cv.waitKey(10) == ord('q'):
        break

cam.release()
cv.destroyAllWindows()
