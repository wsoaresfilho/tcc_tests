# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.button import Button
# Differents logging levels are available : trace, debug, info, warning, error and critical.
from kivy.logger import Logger
 
import cv2
import numpy as np
from realtime import getDetection

# Status colored constants
DEFAULT_STATUS = '[color=2a7cdf]Detecting...[/color]'
DETECTED_STATUS_1 = '[color=32e432]%d objetc found![/color]'
DETECTED_STATUS_2 = '[color=32e432]%d objetcs found![/color]'
 

 # Detection Application class => this is the object detection application
class DetectionApp(Widget):
    def __init__(self, config, goBack, **kwargs):
        super(DetectionApp, self).__init__(**kwargs)
        self.config = config
        self.goBack = goBack

        # Creates an image to handle the camera video
        self.video_img = Image(size_hint=(1,0.8))
        # Creates the button to go back to the menu
        button = Button(text='Back to Menu', font_size=30, background_normal='', background_color=[.5, .2, .2, 1], size_hint=(1,0.1))
        button.bind(on_press=self.btnGoBack)
        # Creates the Status Label
        self.statusbar = Label(text=DEFAULT_STATUS, font_size=30, size_hint=(1,0.1), markup=True)

        # Creates the BoxLayout containing all the widgets
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.video_img)
        self.layout.add_widget(self.statusbar)
        self.layout.add_widget(button)
 
    def build(self):
        return self.layout

    def startJob(self, instance=None):
        Logger.info('Detection: Started Realtime Object Detection!')

        # Creates an object to capture the video
        self.capture = cv2.VideoCapture(self.config.camera_device)
        # Sets the size of the camera image
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.video_width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.video_height)

        # Create a clock to run the video - 30 frames per sec
        self.clock = Clock.schedule_interval(self.updateVideoImage, 1.0/30.0)
 
    def btnGoBack(self, instance):
        Logger.info('Detection: Closing detection!')
        
        # Stop the video clock
        self.clock.cancel()
        # Releases the camera capturing
        self.capture = None
        self.goBack()
 
    def updateVideoImage(self, dt=None):
        # Captures a video frame
        ret, frame = self.capture.read()

        if(ret):
            # Detects objects in the frame image and shows it
            frame, detected_obj_qty = getDetection(frame, self.config)
            # Sets the status in the Status Bar Label
            if(detected_obj_qty > 1):
                print('NUM OBJ DETECTED: %d' %detected_obj_qty)
                self.statusbar.text = DETECTED_STATUS_2 % detected_obj_qty
            elif(detected_obj_qty > 0):
                self.statusbar.text = DETECTED_STATUS_1 % detected_obj_qty
            else:
                self.statusbar.text = DEFAULT_STATUS
         
            # Inverts the image so it not upside down
            flippedFrame = cv2.flip(frame, 0)
            # Converts into a texture to use with kivy
            buf = flippedFrame.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            
            # Updates the image
            self.video_img.texture = texture
