import cv2
import time
from cropimg import crop

cam = cv2.VideoCapture(0)

cam_window = "Take Picture Hitting SPACE!"
cv2.namedWindow(cam_window)

while True:
    # Opens the webcam and show live image
    ret, frame = cam.read()
    cv2.imshow(cam_window, frame)
    if not ret:
        break

    # Read the keyboard
    k = cv2.waitKey(10)

    if k%256 == 27 or k%256 == 113:
        # ESC or 'q' pressed
        print("Escape hit, closing...")
        cam.release()
        break
    elif k%256 == 32:
        # SPACE pressed
        ts = time.time()
        img_name = "../imgsamples/" + "photo_{}.png".format(ts)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))

        # Show photo
        #img = cv2.imread(img_name)
        #cv2.imshow(img_name,img)

        cam.release()
        crop(cam_window, img_name)
        break

cv2.destroyAllWindows()
