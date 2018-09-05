# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
#Differents logging levels are available : trace, debug, info, warning, error and critical.
from kivy.logger import Logger
 
import cv2
import numpy as np
import time
from clearbg import segment
from functools import partial

# Mouse selection status
selection = False
# Empty Regio of Interest Python List
#roi = [x1, y1, x2, y2]
roi = []

class MyImage(Image):
    def on_touch_down(self, touch):
        global roi, selection
        touch.grab(self)
        x, y = touch.pos
        y = Window.height - y
        selection = True
        roi = [x, y, x, y]
    def on_touch_move(self, touch):
        global roi, selection
        if touch.grab_current is self:
            # I received my grabbed touch
            x, y = touch.pos
            if selection == True:
                y = Window.height - y
                roi[2] = x
                roi[3] = y
        
    def on_touch_up(self, touch):
        global roi, selection
        if touch.grab_current is self:
            # I receive my grabbed touch, I must ungrab it!
            selection = False
            x, y = touch.pos
            y = Window.height - y
            roi[2] = x
            roi[3] = y
            touch.ungrab(self)
        else:
            # it's a normal touch
            pass
 
class CropApp(Widget):
    def __init__(self, voltar, config, **kwargs):
        super(CropApp, self).__init__(**kwargs)
        self.voltar = voltar
        self.config = config
        
        #cria uma imagem onde depois iremos inserir a imagem da camera
        self.img_video = MyImage(size_hint=(1,0.8))
        self.img_cut = Image()

        self.button_action = Button(text='Take Photo', font_size=30, background_normal='', background_color=[.1, .3, .7, 1], size_hint=(0.33,1))
        self.button_action.bind(on_press=self.btntakephoto)
        self.button_action2 = Button(text='Save', font_size=30, background_normal='', background_color=[.3, .6, .3, 1], size_hint=(0.33,1))
        self.button_action2.bind(on_press=self.btncropsave)
        self.button_action2.disabled = True
        button_exit = Button(text='Back to Menu', font_size=30, background_normal='', background_color=[.5, .2, .2, 1], size_hint=(0.33,1))
        button_exit.bind(on_press=self.btnexit)

        self.inputLabel = Label(text='[color=2a7cdf]Nome do objeto:[/color]', font_size=30, size_hint=(0.333,1), markup=True)
        self.filename = TextInput(multiline=False, font_size=30, background_color=[.9, .9, .9, .9], padding=15, size_hint=(0.667,1))

        inputLayout = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        inputLayout.add_widget(self.inputLabel)
        inputLayout.add_widget(self.filename)

        btnLayout = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        btnLayout.add_widget(self.button_action)
        btnLayout.add_widget(self.button_action2)
        btnLayout.add_widget(button_exit)

        # aqui criamos um layout  vertical
        self.layout = BoxLayout(orientation='vertical')

        #layout.add_widget(self.img_cut)
        self.layout.add_widget(self.img_video)
        self.layout.add_widget(inputLayout)
        self.layout.add_widget(btnLayout)
 
    def build(self):
        return self.layout

    def startJob(self, instance=None):
        #criamos um objeto de capture de vídeo. Associamos à primeira camera
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,960)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
        Logger.info('Camera: Video Width: %s' %self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        Logger.info('Camera: Video Height: %s' %self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.acionaCamera()
 
    def btntakephoto(self, instance):
        ret, frame = self.capture.read()

        self.clock.cancel()
        self.atualizaImagem(frame)
        self.crop(frame)

    def btncropsave(self, instance=None):
        self.clock.cancel()
        self.saveImage(self.img_cut)
        self.filename.text = ''
        self.btnActionToPhoto()
        self.acionaCamera()

    def crop(self, input_img):
        # Check if image is loaded
        if input_img is not None:
            # Make a copy of original image for cropping
            clone = input_img.copy()
            # Change the action button back to Cam mode
            self.btnActionToCam()
            # Loop
            self.clock = Clock.schedule_interval(partial(self.atualizaCrop, input_img, clone), 1.0/30.0)
        else:
            Logger.warning('Image File: Please Check The Path of Input File')

    def btnActionToCam(self):
        self.button_action.text = "Camera"
        self.button_action.background_color=[.2, .5, .5, 1]
        self.button_action.unbind(on_press=self.btntakephoto)
        self.button_action.bind(on_press = self.acionaCamera)

    def btnActionToPhoto(self):
        self.button_action.text = "Take Photo"
        self.button_action.background_color=[.1, .3, .7, 1]
        self.button_action.unbind(on_press=self.acionaCamera)
        self.button_action.bind(on_press = self.btntakephoto)
        self.button_action2.disabled = True

    def atualizaCrop(self, input_img, clone, dt):
        global roi
        # Cropped Image Window Name
        window_crop_name = 'Cropped Image'

        # if roi has all parameters filled
        if len(roi) == 4:
            # Make a copy of orginal image before drawing rectangle on it
            input_img = clone.copy()
            roi = [int(r) for r in roi]
            # Check if any pixel coordinate is negative and make it zero
            roi = [0 if i < 0 else i for i in roi]
            # Draw rectangle on input_img
            cv2.rectangle(input_img, (roi[0], roi[1]),
                        (roi[2], roi[3]), (0, 255, 0), 2)
            self.atualizaImagem(input_img)
            # Make x and y coordinates for cropping in ascending order
            if roi[0] > roi[2]:
                x1 = roi[2]
                x2 = roi[0]
            else:
                x1 = roi[0]
                x2 = roi[2]
            
            if roi[1] > roi[3]:
                y1 = roi[3]
                y2 = roi[1]
            else:
                y1 = roi[1]
                y2 = roi[3]

            # Crop clone image
            crop_img = clone[y1: y2, x1: x2]
            # check if crop_img is not empty
            if len(crop_img)>4:
                #self.button_action2.disabled = False

                # Create a cropped image Window
                cv2.namedWindow(window_crop_name, cv2.WINDOW_AUTOSIZE)
                # Show image in window
                cv2.imshow(window_crop_name, crop_img)
                self.img_cut = crop_img

            if(cv2.getWindowProperty(window_crop_name, 0) >= 0):
                if(self.filename.text == ''):
                    self.button_action2.disabled = True
                else:
                    self.button_action2.disabled = False
            else:
                self.button_action2.disabled = True
                

        # Check if any key is pressed
        k = cv2.waitKey(1)

        if k == ord('p') or k == 13: # Enter or p
            self.btncropsave()
        elif k == ord('r'):
            if len(crop_img)>4:
                nobg_img = segment(crop_img)
                cv2.imshow(window_crop_name, nobg_img)

    def saveImage(self, img):
        if len(img)>4:
            ts = time.time()
            name = self.filename.text.rstrip().replace(' ', '@')
            img_name = name + "_{}.png".format(ts)
            img_path = "./objimages/" + img_name
            cv2.imwrite(img_path, img)
            Logger.info('Image File: Image saved! => Name: ' + img_name)
            cv2.destroyAllWindows()

    def btnexit(self, instance):
        self.filename.text = ''
        self.btnActionToPhoto()
        self.clock.cancel()
        cv2.destroyAllWindows()
        self.capture = None
        self.config.setDetector()
        self.voltar()

    def acionaCamera(self, instance=None):
        if (not instance == None):
            self.clock.cancel()
            self.filename.text = ''
            self.btnActionToPhoto()

        #criamos um clock para atualizar a imagem a cada 1/320 de segundo
        self.clock = Clock.schedule_interval(self.atualizaVideo, 1.0/30.0)

    def atualizaVideo(self, dt):
        #captura uma imagem da camera
        ret, frame = self.capture.read()
        self.atualizaImagem(frame)
    
    def atualizaImagem(self, frame):
        #inverte para não ficar de cabeça para baixo
        buf1 = cv2.flip(frame, 0)
        # converte em textura
        buf = buf1.tostring()
         
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        
        #apresenta a imagem
        self.img_video.texture = texture1
