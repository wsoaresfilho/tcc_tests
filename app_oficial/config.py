# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.core.window import Window

import cv2 as cv
from myObject import MyObject
from getobjects import getObjects, clearObjects

# Default configuration values
VIDEO_WIDTH=960.0
VIDEO_HEIGHT=540.0
ALGOS_LIST = ['SIFT' , 'SURF', 'ORB', 'BRISK', 'KAZE', 'AKAZE']
FLANN_INDEX_KDITREE=2
MIN_MATCH_COUNT=30
MATCH_DISTANCE=0.75

# Function that returns the detector and the matcher by the index
def getDetector(index):
    ALGO_TYPE = index
    if(ALGO_TYPE == 0):
        detector=cv.xfeatures2d.SIFT_create()
    elif(ALGO_TYPE == 1):
        detector=cv.xfeatures2d.SURF_create()
    elif(ALGO_TYPE == 2):
        detector=cv.ORB_create(nfeatures=1000, scaleFactor = 1.2, WTA_K = 2, scoreType=cv.ORB_FAST_SCORE)
    elif(ALGO_TYPE == 3):
        detector=cv.BRISK_create()
    elif(ALGO_TYPE == 4):
        detector=cv.KAZE_create()
    elif(ALGO_TYPE == 5):
        detector=cv.AKAZE_create()

    if(ALGO_TYPE == 0 or ALGO_TYPE == 1 or ALGO_TYPE == 4):
        flannParam=dict(algorithm=FLANN_INDEX_KDITREE,tree=5)
        matcher=cv.FlannBasedMatcher(flannParam,{})
    elif(ALGO_TYPE == 2 or ALGO_TYPE == 3 or ALGO_TYPE == 5):
        matcher=cv.BFMatcher(cv.NORM_HAMMING)

    return (detector, matcher)


# Configuration: a BoxLayout containing all the configs
class Config(BoxLayout):
    def __init__(self, goBack, **kwargs):
        super(Config, self).__init__(**kwargs)
        self.goBack = goBack
        label_size = 30
        label_hint_x = 0.5

        self.video_width = VIDEO_WIDTH
        self.video_height = VIDEO_HEIGHT

        self.detector_index = 3 # Using BRISK as default value
        self.setDetector()

        # Creating the Detector Dropdown
        detectorLabel = Label(text='Choose the detection algorithm:', font_size=label_size, size_hint=(label_hint_x, 0.1))
        self.detector_dropdown = DropDown(color = (1,1,1,1))
        for index, algo in enumerate(ALGOS_LIST):
            btn = Button(text='%s' % algo, size_hint_y = None, height = 44)
            btn.bind(on_release=self.setDetectorDropdown)
            self.detector_dropdown.add_widget(btn)

        mainbutton = Button(text=ALGOS_LIST[self.detector_index], size_hint=(label_hint_x,.1))
        mainbutton.bind(on_release=self.detector_dropdown.open)
        self.detector_dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

        # Creating the min number of matches config
        matchesLabel = Label(text='Minimum number of matches:', font_size=label_size, size_hint=(label_hint_x,0.1))
        self.minMatches = TextInput(text=str(MIN_MATCH_COUNT), multiline=False, input_filter='int', font_size=label_size, background_color=[.9, .9, .9, .9], padding=10, size_hint=(0.5,0.1))

        # Creating the good match distance config
        distanceLabel = Label(text='Good match distance:', font_size=label_size, size_hint=(label_hint_x,0.1))
        self.distance = TextInput(text=str(MATCH_DISTANCE), multiline=False, input_filter='float', font_size=label_size, background_color=[.9, .9, .9, .9], padding=10, size_hint=(0.5,0.1))

        # Creating the play audio(TTS) checkbox config
        self.playAudio = False
        audioLabel = Label(text='Enable TTS (Audio):', font_size=label_size, size_hint=(label_hint_x, 0.1))
        checkbox_audio = CheckBox(value=self.playAudio, color=(1,1,1,1), size_hint=(.5, 0.1))
        checkbox_audio.bind(active=self.setAudio)

        # Creating the show center circles config
        self.showCenterCircles = False
        circlesLabel = Label(text='Show centered circles:', font_size=label_size, size_hint=(label_hint_x, 0.1))
        checkbox_circles = CheckBox(value=self.showCenterCircles, color=(1,1,1,1), size_hint=(.5, 0.1))
        checkbox_circles.bind(active=self.setCircles)

        # Creating the button for clearing all the objetcs (images) from the obj folder
        btn_clear = Button(text='Clear Objects', font_size=30, background_normal='', background_color=[.8, .2, .2, 1], size_hint=(1, 0.1))
        btn_clear.bind(on_press=self.btnclear)
        
        # Creating the go back to menu button
        btn_back = Button(text='Back to Menu', font_size=30, background_normal='', background_color=[.5, .2, .2, 1], size_hint=(1, 0.1))
        btn_back.bind(on_press=self.btnquit)

        # Adding every widget to the layout
        config_area = StackLayout(size_hint=(1,.8))
        config_area.add_widget(detectorLabel)
        config_area.add_widget(mainbutton)
        config_area.add_widget(matchesLabel)
        config_area.add_widget(self.minMatches)
        config_area.add_widget(distanceLabel)
        config_area.add_widget(self.distance)
        config_area.add_widget(audioLabel)
        config_area.add_widget(checkbox_audio)
        config_area.add_widget(circlesLabel)
        config_area.add_widget(checkbox_circles)

        self.add_widget(config_area)
        self.add_widget(btn_clear)
        self.add_widget(btn_back)

        self.orientation = 'vertical'
        with self.canvas.before:
            Color(.1, .2, .9, .3)
            Rectangle(size=Window.size)

    def setDetectorDropdown(self, instance=None):
        self.detector_dropdown.select(instance.text)
        self.detector_index = ALGOS_LIST.index(instance.text)
        self.setDetector()

    def setDetector(self):
        self.detector = getDetector(self.detector_index)
        detector, matcher = self.detector
        self.list_objects=[]

        # Get all the object dictionaries (name, image)
        images = getObjects()
        # Create all the objects based on the images from the folder
        for image in images:
            self.list_objects.append(MyObject(image['name'], image['images'], detector))

    def setAudio(self, checkbox, value):
        if value:
            self.playAudio = True
        else:
            self.playAudio = False

    def setCircles(self, checkbox, value):
        if value:
            self.showCenterCircles = True
        else:
            self.showCenterCircles = False

    def btnclear(self, instance):
        clearObjects()

    def btnquit(self, instance):
        self.goBack()
