# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.button import Button
#Differents logging levels are available : trace, debug, info, warning, error and critical.
from kivy.logger import Logger
 
import cv2
import numpy as np
from realtime import getDetection

DEFAULT_STATUS = '[color=2a7cdf]Detecting...[/color]'
DETECTED_STATUS_1 = '[color=32e432]%d objetc found![/color]'
DETECTED_STATUS_2 = '[color=32e432]%d objetcs found![/color]'
 
class DetectionApp(Widget):
    def __init__(self, config, voltar, **kwargs):
        super(DetectionApp, self).__init__(**kwargs)
        self.config = config
        self.voltar = voltar

        #cria uma imagem onde depois iremos inserir a imagem da camera
        self.img1 = Image(size_hint=(1,0.8))
        button = Button(text='Back to Menu', font_size=30, background_normal='', background_color=[.5, .2, .2, 1], size_hint=(1,0.1))
        button.bind(on_press=self.btncallback)
        self.statusbar = Label(text=DEFAULT_STATUS, font_size=30, size_hint=(1,0.1), markup=True)

        #aqui criamos um layout  vertical
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.img1)
        self.layout.add_widget(self.statusbar)
        self.layout.add_widget(button)
 
    def build(self):
        return self.layout

    def startJob(self, instance=None):
        Logger.info('Detection: Started Realtime Object Detection!')

        #criamos um objeto de capture de vídeo. Associamos à primeira camera
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,960)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,540)

        #criamos um clock para atualizar a imagem a cada 1/320 de segundo
        self.clock = Clock.schedule_interval(self.atualizaImagem, 1.0/30.0)
 
    def btncallback(self, instance):
        Logger.info('Detection: Closing detection!')
        
        self.clock.cancel()
        self.capture = None
        self.voltar()
 
    def atualizaImagem(self, dt=None):
        #captura uma imagem da camera
        ret, frame = self.capture.read()
        if(ret):
            frame, detected_obj_qty = getDetection(frame, self.config)
            if(detected_obj_qty > 1):
                print('NUM OBJ DETECTED: %d' %detected_obj_qty)
                self.statusbar.text = DETECTED_STATUS_2 % detected_obj_qty
            elif(detected_obj_qty > 0):
                self.statusbar.text = DETECTED_STATUS_1 % detected_obj_qty
            else:
                self.statusbar.text = DEFAULT_STATUS
         
            #inverte para não ficar de cabeça para baixo
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring() # converte em textura
            
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            
            self.img1.texture = texture1 #apresenta a imagem
