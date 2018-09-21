# -*- coding: utf-8 -*-

from kivy.config import Config
# Setup Window size
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 675
Config.set('graphics', 'width', WINDOW_WIDTH)
Config.set('graphics', 'height', WINDOW_HEIGHT)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from cropApp import CropApp
from detectionApp import DetectionApp
from config import Config
from getobjects import objectsExist
from kivy.clock import Clock

# Creating the main menu screen with kivy language
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        id: boxmain
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: .1, .3, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            id: boxtitle
            height: "250dp"
            size_hint_y: None
            Label:
                text: 'Object Detection App'
                font_size: 58

        BoxLayout:
            id: boxbtn
            orientation: 'vertical'
            height: "300dp"
            width: "500dp"
            size_hint_y: None
            size_hint_x: None
            pos_hint: {'center_x': 0.5}

            Button:
                id: btndetect
                text: 'Detect Objects'
                on_press: app.detect()
                font_size: 28
                disabled: root.hasNoObjects()
            Button:
                id: btnadd
                text: 'Add Object'
                on_press: app.crop()
                font_size: 28
            Button:
                id: btnconfig
                text: 'Configuration'
                on_press: root.manager.current = 'config'
                font_size: 28
            Button:
                id: btnquit
                text: 'Quit'
                on_press: app.stop()
                font_size: 28

        BoxLayout:
            Label:
                text: ''
                font_size: 36
""")

# Declare screens classes
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.clock = Clock.schedule_interval(self.atualiza, 0.5)

    def atualiza(self, dt):
        self.disable = hasEmptyObjects()
        self.ids.btndetect.disabled = self.disable

    def hasNoObjects(self):
        self.disable = hasEmptyObjects()
        return self.disable

class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)
        self.add_widget(config_app)

class DetectObjScreen(Screen):
    def __init__(self, **kwargs):
        super(DetectObjScreen, self).__init__(**kwargs)
        self.add_widget(detect_app.build())

class AddObjScreen(Screen):
    def __init__(self, **kwargs):
        super(AddObjScreen, self).__init__(**kwargs)
        self.add_widget(crop_app.build())

# Function to verify if the objects folder is empty
def hasEmptyObjects():
    return not objectsExist()

# Function to go back to the main menu screen
def goBackToMenu():
    global sm
    sm.current = 'menu'
    sm.transition.direction = 'right'

# Initialize Apps
config_app = Config(goBackToMenu)
detect_app = DetectionApp(config_app, goBackToMenu)
crop_app = CropApp(goBackToMenu, config_app)

# Create the screen manager and add all the screens
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(ConfigScreen(name='config'))
sm.add_widget(DetectObjScreen(name='detection'))
sm.add_widget(AddObjScreen(name='addobj'))

# MainApp class
class MainApp(App):
    title = 'Object Detection App'

    def detect(self):
        sm.current = 'detection'
        detect_app.startJob()

    def crop(self):
        sm.current = 'addobj'
        crop_app.startJob()

    def build(self):
        return sm

if __name__ == '__main__':
    MainApp().run()
