#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
 
import cv2
import numpy as np
 
class CameraApp(App):
 
    def build(self):
        self.img1 = Image()   #cria uma imagem onde depois iremos inserir a imagem da camera
        label1= Label(text="Experimentos com vídeo (II)")  #label superior
        label2= Label(text="www.cadernodelaboratorio.com.br") #label inferior
        layout = BoxLayout(orientation='vertical')  #|aqui criamos um layout  vertical
        #layout.add_widget(label1)   #inserimos os widgets segundo a ordem que desejamos apresentá-los na tela
        layout.add_widget(self.img1)  
        #layout.add_widget(label2)
         
        self.capture = cv2.VideoCapture(0)  #criamos um objeto de capture de vídeo. Associamos à primeira camera
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,1024)

        ret, frame = self.capture.read() #criamos um frame com esta imagem
        #cv2.namedWindow("CV2 Image")     #nome da janela
        #cv2.imshow("CV2 Image", frame)
        Clock.schedule_interval(self.atualizaImagem, 1.0/30.0)   #criamos um clock para atualizar a imagem a cada 1/320 de segundo
        return layout
 
     
 
    def atualizaImagem(self, dt):
        ret, frame = self.capture.read()   #captura uma imagem da camera
         
        buf1 = cv2.flip(frame, 0)   #inverte para não ficar de cabeça para baixo
        buf = buf1.tostring() # converte em textura
         
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
         
        self.img1.texture = texture1 #apresenta a imagem
 
if __name__ == '__main__':
    CameraApp().run()