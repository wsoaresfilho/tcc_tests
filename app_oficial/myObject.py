import cv2 as cv
from random import randint

class MyObject:
    def __init__(self, obj_name, img_array, detector):
        self.file_names=img_array
        self.name=obj_name
        self.color=(randint(0, 255), randint(0, 255), randint(0, 255))
        self.objImages=[]
        self.objKeyPoints=[]
        self.objDescriptors=[]

        for image in img_array:
            self.appendObjImages(image, detector)

    def appendObjImages(self, image, detector):
        image=cv.imread(image, 0)
        self.objImages.append(image)
        kp,descriptor=detector.detectAndCompute(image, None)
        self.appendObjKPs(kp)
        self.appendObjDescriptors(descriptor)

    def appendObjKPs(self, kp):
        self.objKeyPoints.append(kp)
        
    def appendObjDescriptors(self, descriptor):
        self.objDescriptors.append(descriptor)