import cv2
import time
from clearbg import segment

# Mouse selection status
selection = False
# Empty Regio of Interest Python List
#roi = [x1, y1, x2, y2]
roi = []

# Mouse Callback for ROI selection
# event: The event that took place (left mouse button pressed, left mouse button released, mouse movement, etc).
# x: The x-coordinate of the event.
# y: The y-coordinate of the event.
# flags: Any relevant flags passed by OpenCV.
# params: Any extra parameters supplied by OpenCV.
def roi_selection(event, x, y, flags, param):
    # Refernce to the global variables
    global selection, roi
    # On Left mouse button click records roi with mouse selection status to True
    if event == cv2.EVENT_LBUTTONDOWN:
        selection = True
        roi = [x, y, x, y]
    # On Mouse movement records roi with mouse selection status to True
    elif event == cv2.EVENT_MOUSEMOVE:
        if selection == True:
            roi[2] = x
            roi[3] = y

    # If Left mouse button is released changes mouse selection status to False
    elif event == cv2.EVENT_LBUTTONUP:
        selection = False
        roi[2] = x
        roi[3] = y

def crop(win_name, image_path):
    # Uses the roi global variable
    global roi

    # Path of image file to be read
    #image_read_path = './elisa.jpg'
    image_read_path = image_path

    # Original Image Window Name
    #window_name = 'Input Image'
    window_name = win_name

    # Cropped Image Window Name
    window_crop_name = 'Cropped Image'

    # Escape ASCII Keycode
    esc_keycode = 27
    enter_keycode = 13

    # Time to waitfor
    wait_time = 1

    # Load an image
    # cv2.IMREAD_COLOR = Default flag for imread. Loads color image.
    # cv2.IMREAD_GRAYSCALE = Loads image as grayscale.
    # cv2.IMREAD_UNCHANGED = Loads image which have alpha channels.
    # cv2.IMREAD_ANYCOLOR = Loads image in any possible format
    # cv2.IMREAD_ANYDEPTH = Loads image in 16-bit/32-bit otherwise converts it to 8-bit
    input_img = cv2.imread(image_read_path, cv2.IMREAD_ANYCOLOR)

    # Check if image is loaded
    if input_img is not None:
        # Make a copy of original image for cropping
        clone = input_img.copy()
        # Create a Window
        # cv2.WINDOW_NORMAL = Enables window to resize.
        # cv2.WINDOW_AUTOSIZE = Default flag. Auto resizes window size to fit an image.
        #cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        # Set mouse handler for Window with roi_selection function callback
        cv2.setMouseCallback(window_name, roi_selection)

        # Loop
        while True:
            # Show original image in window
            cv2.imshow(window_name, input_img)

            # if roi has all parameters filled
            if len(roi) == 4:
                # Make a copy of orginal image before drawing rectangle on it
                input_img = clone.copy()
                # Check if any pixl coorinalte is negative and make it zero
                roi = [0 if i < 0 else i for i in roi]
                # Draw rectangle on input_img
                # input_image: source image
                # (roi[0], roi[1]): Vertex of the rectangle
                # (roi[2], roi[3]): Opposite Vertex of the rectangle
                # (0, 255, 0): Rectangular Color
                # 2: Thickness
                cv2.rectangle(input_img, (roi[0], roi[1]),
                              (roi[2], roi[3]), (0, 255, 0), 2)
                # Make x and y coordiates for cropping in ascending order
                # if x1 = 200,x2= 10 make x1=10,x2=200
                if roi[0] > roi[2]:
                    x1 = roi[2]
                    x2 = roi[0]
                # else keep it as it is
                else:
                    x1 = roi[0]
                    x2 = roi[2]
                # if y1 = 200,y2= 10 make y1=10,y2=200
                if roi[1] > roi[3]:
                    y1 = roi[3]
                    y2 = roi[1]
                # else keep it as it is
                else:
                    y1 = roi[1]
                    y2 = roi[3]

                # Crop clone image
                crop_img = clone[y1: y2, x1: x2]
                # check if crop_img is not empty
                if len(crop_img)>4:
                    # Create a cropped image Window
                    cv2.namedWindow(window_crop_name, cv2.WINDOW_AUTOSIZE)
                    # Show image in window
                    cv2.imshow(window_crop_name, crop_img)

            # Check if any key is pressed
            k = cv2.waitKey(wait_time)
            # Check if ESC key is pressed. ASCII Keycode of ESC=27
            if k == esc_keycode or k == ord('q'):
                # Destroy All Windows
                cv2.destroyAllWindows()
                break
            elif k == ord('p') or k == enter_keycode:
                if len(crop_img)>4:
                    ts = time.time()
                    img_name = "../imgsamples/" + "photo_cropped_{}.png".format(ts)
                    cv2.imwrite(img_name, crop_img)
                    print("Cropped image saved! => Name: " + img_name)
            elif k == ord('r'):
                if len(crop_img)>4:
                    nobg_img = segment(crop_img)
                    cv2.imshow(window_crop_name, nobg_img)

    else:
        print 'Please Check The Path of Input File'
