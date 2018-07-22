import cv2 as cv
from random import randint

detector=cv.xfeatures2d.SIFT_create()

class Objeto:
    def __init__(self, obj_name, img_array):
        self.file_names=img_array
        self.name=obj_name
        self.color=(randint(0, 255), randint(0, 255), randint(0, 255))
        self.trainImgs=[]
        self.trainKPs=[]
        self.trainDescs=[]

        for image in img_array:
            self.appendTrainImages(image)

    def appendTrainImages(self, image):
        trainImage=cv.imread(image,0)
        self.trainImgs.append(trainImage)
        trainKP,trainDesc=detector.detectAndCompute(trainImage,None)
        self.appendTrainKPs(trainKP)
        self.appendtrainDescs(trainDesc)

    def appendTrainKPs(self, trainKP):
        self.trainKPs.append(trainKP)
    def appendtrainDescs(self, trainDesc):
        self.trainDescs.append(trainDesc)