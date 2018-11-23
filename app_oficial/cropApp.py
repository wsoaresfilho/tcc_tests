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
from clearbg import bgSegmentation
from functools import partial

# Mouse selection status
selection = False
# Region Of Interest => will contain the coordinates for the selection
roi = []
# Keep the video size to calculate the difference if window and video size
VIDEO_WIDTH = 0
VIDEO_HEIGHT = 0

# Custom image class that handles the mouse events to do the cropping
class MyImage(Image):
    def on_touch_down(self, touch):
        global roi, selection, VIDEO_WIDTH, VIDEO_HEIGHT
        touch.grab(self)
        x, y = touch.pos
        y = Window.height - ((Window.height*0.8 - VIDEO_HEIGHT)/2) - y
        x = x - (Window.width - VIDEO_WIDTH)/2
        selection = True
        roi = [x, y, x, y]

    def on_touch_move(self, touch):
        global roi, selection, VIDEO_WIDTH, VIDEO_HEIGHT
        if touch.grab_current is self:
            x, y = touch.pos
            if selection == True:
                y = Window.height - ((Window.height*0.8 - VIDEO_HEIGHT)/2) - y
                x = x - (Window.width - VIDEO_WIDTH)/2
                roi[2] = x
                roi[3] = y
        
    def on_touch_up(self, touch):
        global roi, selection, VIDEO_WIDTH, VIDEO_HEIGHT
        if touch.grab_current is self:
            selection = False
            x, y = touch.pos
            y = Window.height - ((Window.height*0.8 - VIDEO_HEIGHT)/2) - y
            x = x - (Window.width - VIDEO_WIDTH)/2
            roi[2] = x
            roi[3] = y
            touch.ungrab(self)

# Crop Application Class => does the image cropping 
class CropApp(Widget):
    def __init__(self, goBack, config, **kwargs):
        super(CropApp, self).__init__(**kwargs)
        self.goBack = goBack
        self.config = config
        
        # Creates an image objetc that will contain the video/photo and will be cropped
        self.img_video = MyImage(size_hint=(1,0.8))
        # Crates an image object that will contain the new cropped image
        self.img_cut = Image()

        # Creates the action buttons
        self.photo_action_btn = Button(text='Take Photo', font_size=30, background_normal='', background_color=[.1, .3, .7, 1], size_hint=(0.33,1))
        self.photo_action_btn.bind(on_press=self.btntakephoto)
        self.save_action_btn = Button(text='Save', font_size=30, background_normal='', background_color=[.3, .6, .3, 1], size_hint=(0.33,1))
        self.save_action_btn.bind(on_press=self.btncropsave)
        self.save_action_btn.disabled = True
        button_exit = Button(text='Back to Menu', font_size=30, background_normal='', background_color=[.5, .2, .2, 1], size_hint=(0.33,1))
        button_exit.bind(on_press=self.btnexit)

        # Creates the obj name input area
        inputLabel = Label(text='[color=2a7cdf]Object name:[/color]', font_size=30, size_hint=(0.333,1), markup=True)
        self.obj_file_name = TextInput(multiline=False, font_size=30, background_color=[.9, .9, .9, .9], padding=15, size_hint=(0.667,1))

        # Creates a BoxLayout to contain the obj name input
        inputLayout = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        inputLayout.add_widget(inputLabel)
        inputLayout.add_widget(self.obj_file_name)

        # Creates a BoxLayout to contain all the buttons
        btnLayout = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        btnLayout.add_widget(self.photo_action_btn)
        btnLayout.add_widget(self.save_action_btn)
        btnLayout.add_widget(button_exit)

        # Creates the main BoxLayout that contains everything
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.img_video)
        self.layout.add_widget(inputLayout)
        self.layout.add_widget(btnLayout)
 
    def build(self):
        return self.layout

    def startJob(self, instance=None):
        global VIDEO_WIDTH, VIDEO_HEIGHT
        # Creates a video capturing
        self.videoCapture = cv2.VideoCapture(self.config.camera_device)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.video_width)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.video_height)
        Logger.info('Camera: Video Width: %s' %self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        Logger.info('Camera: Video Height: %s' %self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Sets the real video size to calculate the difference between the video and the window
        VIDEO_HEIGHT = self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        VIDEO_WIDTH = self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.initializeCamera()
 
    def btntakephoto(self, instance):
        # Get a frame from the video image
        ret, frame = self.videoCapture.read()
        # Stops the clock that runs the video
        self.clock.cancel()
        # Shows the frame in the window replacing the video
        self.showImage(frame)
        # Does the cropping magic
        self.crop(frame)

    def btncropsave(self, instance=None):
        # Stops the clock that had the crop magic going on
        self.clock.cancel()
        # Saves the cropped image
        self.saveImage(self.img_cut)
        # Clears the obj name input
        self.obj_file_name.text = ''
        # Changes the action button back to the Take a Photo mode
        self.btnActionSetToTakePhotoMode()
        # Initializes the Camera and shows it
        self.initializeCamera()

    def crop(self, input_img):
        # Check if image is loaded
        if input_img is not None:
            # Make a copy of original image for cropping
            clone = input_img.copy()
            # Change the action button back to Cam mode
            self.btnActionSetToCameraMode()
            # Starts the clock/loop to wait for the cropping
            self.clock = Clock.schedule_interval(partial(self.createCropImage, input_img, clone), 1.0/30.0)
        else:
            Logger.warning('Image File: Please Check The Path of Input File')

    def btnActionSetToCameraMode(self):
        # Changes the action button back to the Camera mode
        self.photo_action_btn.text = "Camera"
        self.photo_action_btn.background_color=[.2, .5, .5, 1]
        self.photo_action_btn.unbind(on_press=self.btntakephoto)
        self.photo_action_btn.bind(on_press = self.initializeCamera)

    def btnActionSetToTakePhotoMode(self):
        # Changes the action button back to the Take Photo mode
        self.photo_action_btn.text = "Take Photo"
        self.photo_action_btn.background_color=[.1, .3, .7, 1]
        self.photo_action_btn.unbind(on_press=self.initializeCamera)
        self.photo_action_btn.bind(on_press = self.btntakephoto)
        self.save_action_btn.disabled = True

    def createCropImage(self, input_img, clone, dt):
        global roi
        # Cropped Image Window Name
        window_crop_name = 'Cropped Image'

        # if roi has all parameters filled
        if len(roi) == 4:
            # Make a copy of orginal image before drawing rectangle on it
            input_img = clone.copy()
            # Converts all the coordinates into integers numbers
            roi = [int(r) for r in roi]
            # Check if any pixel coordinate is negative and make it zero
            roi = [0 if i < 0 else i for i in roi]
            # Draw rectangle on input_img
            cv2.rectangle(input_img, (roi[0], roi[1]),
                        (roi[2], roi[3]), (0, 255, 0), 2)
            # Show the image with the rectangle on it
            self.showImage(input_img)
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

            # Create a cropped image Window
            cv2.namedWindow(window_crop_name, cv2.WINDOW_AUTOSIZE)

            # Crop clone image
            crop_img = clone[y1: y2, x1: x2]
            # check if crop_img is not empty
            if len(crop_img)>4:
                # Show image in window
                cv2.imshow(window_crop_name, crop_img)
                self.img_cut = crop_img

            # Creates a validation to only enable the Save button if there is already a name to the object
            if(cv2.getWindowProperty(window_crop_name, 0) >= 0):
                if(self.obj_file_name.text == ''):
                    self.save_action_btn.disabled = True
                else:
                    self.save_action_btn.disabled = False
            else:
                self.save_action_btn.disabled = True
                

        # Captures a key press
        k = cv2.waitKey(1)
        # If ENTER or "p" is pressed we save the cropped image
        if k == ord('p') or k == 13:
            self.btncropsave()
        # else if the "r" is pressed, we Remove the background of the cropped image
        elif k == ord('r'):
            if len(crop_img)>4:
                nobg_img = bgSegmentation(crop_img) # This removes the image background
                cv2.imshow(window_crop_name, nobg_img)

    def saveImage(self, img):
        # Saves the image file based on the name given
        if len(img)>4:
            ts = time.time()
            # Lets do a trick to save names with empty spaces on it
            name = self.obj_file_name.text.rstrip().replace(' ', '@')
            img_name = name + "_{}.png".format(ts)
            img_path = "./objimages/" + img_name
            cv2.imwrite(img_path, img) # Saves the image file
            Logger.info('Image File: Image saved! => Name: ' + img_name)
            cv2.destroyAllWindows() # Close the cropped image preview window

    def btnexit(self, instance):
        # Sets everything back to default state when exit
        self.obj_file_name.text = ''
        self.btnActionSetToTakePhotoMode()
        self.clock.cancel()
        cv2.destroyAllWindows()
        self.videoCapture = None
        self.config.setDetector()
        self.goBack()

    def initializeCamera(self, instance=None):
        if (not instance == None):
            self.clock.cancel()
            self.obj_file_name.text = ''
            self.btnActionSetToTakePhotoMode()

        # Lets create a clock/loop to show the video camera
        self.clock = Clock.schedule_interval(self.updateVideoImage, 1.0/30.0)

    def updateVideoImage(self, dt):
        # Captures the video frame and shows it
        ret, frame = self.videoCapture.read()
        self.showImage(frame)
    
    def showImage(self, frame):
        # Inverts the image so it not upside down
        flippedFrame = cv2.flip(frame, 0)
        # Converts into a texture to use with kivy
        buf = flippedFrame.tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # Shows the image on screen
        self.img_video.texture = texture
