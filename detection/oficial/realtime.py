import cv2 as cv
import numpy as np
from objeto import Objeto

# Constants of configuration
MIN_MATCH_COUNT=40
SIMULATE_REAL_DEVICE=True
FLANN_INDEX_KDITREE=0
VIDEO_WIDTH=960.0
VIDEO_HEIGHT=540.0

# Informacoes que devem ser cadastradas e salvas em BD
objetos=[]
images=[["unizinco.jpg", "unizinco2.jpg", "unizinco3.jpg"], ["rinosoro.jpg"]]
img_names=["unizinco", "rinosoro"]

# Criacao dos objetos
for index,imageArray in enumerate(images):
    objetos.append(Objeto(img_names[index], imageArray))

# Inicializacao da camera
cam=cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)

detector=cv.xfeatures2d.SIFT_create()

flannParam=dict(algorithm=FLANN_INDEX_KDITREE,tree=5)
flann=cv.FlannBasedMatcher(flannParam,{})

while True:
    ret, QueryImgBGR=cam.read()
    QueryImg=cv.cvtColor(QueryImgBGR,cv.COLOR_BGR2GRAY)
    queryKP,queryDesc=detector.detectAndCompute(QueryImg,None)
    
    # Percorre os objetos e os seus descritores
    for i,objeto in enumerate(objetos):
        for j,td in enumerate(objeto.trainDescs):
            goodMatch=[]
            matches=flann.knnMatch(queryDesc,td,k=2)

            for m,n in matches:
                if(m.distance<0.70*n.distance):
                    goodMatch.append(m)
    
            if(len(goodMatch)>MIN_MATCH_COUNT):
                tp=[]
                qp=[]
                for m in goodMatch:
                    tp.append(objeto.trainKPs[j][m.trainIdx].pt)
                    qp.append(queryKP[m.queryIdx].pt)
                tp,qp=np.float32((tp,qp))
                H,status=cv.findHomography(tp,qp,cv.RANSAC,3.0)
                h,w=objeto.trainImgs[j].shape
                trainBorder=np.float32([[[0,0],[0,h-1],[w-1,h-1],[w-1,0]]])
                queryBorder=cv.perspectiveTransform(trainBorder,H)
                corners=np.int32(queryBorder)
                # Desenha o quadrado ao redor do objeto
                cv.polylines(QueryImgBGR, [np.int32(queryBorder)], True, objeto.color, 3)
                # Escreve o texto do objeto
                cv.putText(QueryImgBGR, objeto.name, (corners[0][0][0], corners[0][0][1]-10), 2, 1, objeto.color, 2)
            else:
                print "Not Enough match found for object %d- %d/%d"%(i+1,len(goodMatch),MIN_MATCH_COUNT)

    if SIMULATE_REAL_DEVICE:
        videoWidth = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
        videoHeight = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))
        #print "Video: Width: %d, Height: %d"%(videoWidth, videoHeight)
        cv.circle(QueryImgBGR,(videoWidth/2,videoHeight/2), videoHeight/3, (0,0,255), 1)

    # Abre a janela com o video
    cv.imshow('Reconhecimento de Objetos', QueryImgBGR)
    # Para sair pressione a tecla "q"
    if cv.waitKey(10)==ord('q'):
        break

cam.release()
cv.destroyAllWindows()

