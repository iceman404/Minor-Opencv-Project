import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from google.protobuf.json_format import MessageToDict
import numpy as np
import time
import tensorflow as tf
#from tensorflow.keras.models import load_model
from pynput.keyboard import Key, Controller
import subprocess



cap = cv2.VideoCapture(1)
x, y = 1920, 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, x)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y)
#cap.set(90,100)
# Checks for camera

mpHands = mp.solutions.hands  # detects hand/finger
hands = mpHands.Hands(max_num_hands=2,min_detection_confidence=0.7)  # complete the initialization configuration of hands
mpDraw = mp.solutions.drawing_utils
finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_Coord = (4,2)

# To access speaker through the library pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#model = load_model('mp_hand_gesture')
#f = open('gesture.names', 'r')
#classNames = f.read().split('\n')
#f.close()
#print(classNames)
volbar = 700
process1_flag = 4
volper = 0
blbar = 400
blper = 0
volMin, volMax = volume.GetVolumeRange()[:2]
blMin = 10
blMax = 100
ptime = 0
newTime = 0
timer = 0
flag=0
counting = False
cooldown = 0
direction = "none"
keyboard = Controller()

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)# If camera works capture an image
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to rgb
    # update time and counter
    newTime = time.time()
    if counting:
        timer += newTime - ptime

    fps = 1 / (newTime - ptime)
    ptime = newTime
    img.flags.writeable = False
    results = hands.process(imgRGB)
    img.flags.writeable = True
    # get hand landmarks
  #  lmList = findPosition(results, img)
    cv2.line(img, (400, 0), (400, 728), (255, 0, 255), thickness=2)
    cv2.line(img, (x - 1000, 0), (x - 1000, 728), (255, 0, 255), thickness=2)
    # if cooldown:
    cv2.putText(img, f'timer: {int(timer)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    cv2.putText(img, f'cooldown: {int(cooldown)}', (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

    # Collection of gesture information
    results = hands.process(imgRGB)  # completes the image processing.
    #className = ''

    lmList = []  # empty list
    if results.multi_hand_landmarks:  # list of all hands detected.
        handList = []
        # By accessing the list, we can get the information of each hand's corresponding flag bit
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):  # adding counter and returning it
                # Get finger joint points
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                handList.append((cx,cy))
                lmList.append([id, cx, cy])  # adding to the empty list 'lmList'
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)
            for point in handList:
                cv2.circle(img, point, 5, (255, 255, 255), cv2.FILLED)



    if lmList != []:
        # getting the value at a point
        # x      #y
        x1, y1 = lmList[4][1], lmList[4][2]  # thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # index finger
        x3, y3 = lmList[12][1], lmList[12][2] #middle finger
        x4, y4 = lmList[16][1], lmList[16][2] #ring finger
        x5, y5 = lmList[20][1], lmList[20][2]  # pinky finger
        # creating circle at the tips of thumb and index finger
        cv2.circle(img, (x1, y1), 15, (67, 168, 25), cv2.FILLED)
        cv2.circle(img, (x3, y3), 15, (67, 222, 255), cv2.FILLED)  # image #fingers #radius #rgb
        cv2.circle(img, (x4, y4), 15, (111, 200, 155), cv2.FILLED)
        cv2.circle(img, (x5, y5), 15, (137, 20, 150), cv2.FILLED)
        # trigger to right
        if (x3 < 400 or x4 < 400 or x5 < 400) and cooldown == 0 and direction == "none":
            counting = True
            timer = 0
            direction = "right"

        # trigger to left
        if (x3 > x - 1000 or x4 > x - 1000 or x5 > x - 1000) and cooldown == 0 and direction == "none":
            counting = True
            timer = 0
            direction = "left"

        # check if swipped right
        if (x3 > x - 1000 or x4 > x - 1000 or x5 > x - 1000) and timer < 1.5 and direction == "right":
            print("Swipped right")
            keyboard.press(Key.left)
            keyboard.release(Key.left)
            cooldown = 5
            timer = 0
            direction = "none"
            flag = 4

        # check if swipped left
        if (x3 < 400 or x4 < 400 or x5 < 400) and timer < 1.5 and direction == "left":
            print("Swipped left")
            keyboard.press(Key.right)
            keyboard.release(Key.right)
            timer = 0
            cooldown = 5
            direction = "none"
            flag = 2




            # ================ timer reset of 1 seconds ===================


        if len(results.multi_handedness) != 2:

            for i in results.multi_handedness:
                label = MessageToDict(i)['classification'][0]['label']

                if label == 'Left':

                    cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)  # image #fingers #radius #rgbb
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # create a line b/w tips of middle finger and thumb
                    cv2.putText(img, label + ' Hand',(20, 300),cv2.FONT_HERSHEY_PLAIN,2, (0, 255, 0), 2)

                    #prediction = model.predict([handList])
                    #print(prediction)
                    #classID = np.argmax(prediction)
                    #className = classNames[classID]
                   # # show the prediction on the frame
                   # cv2.putText(img, className, (550, 150), cv2.FONT_HERSHEY_PLAIN,
                    #            3, (160, 220, 255), 3)
                    #if(process1_flag == 0):
                    #p1 = subprocess()
                   # global p1
                    #if (className == 'thumbs up' and process1_flag == 4):
                     #  p1 = subprocess.Popen('C:\Program Files\LibreOffice\program\simpress.exe')
                       # process1_flag = 5
                    #if (className == 'fist' and process1_flag == 5):
                       # p1.kill()
                       # process1_flag = 4



                    upCount = 0
                    for coordinate in finger_Coord:
                        if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                            upCount += 1
                    if handList[thumb_Coord[0]][0] > handList[thumb_Coord[1]][0]:
                        upCount += 1
                    cv2.putText(img, f'Finger Count: {str(upCount)}', (540, 90), cv2.FONT_HERSHEY_PLAIN, 2, (133, 15, 59), 2)

                    if (upCount == 2):
                        length = hypot(x2 - x1, y2 - y1)  # distance b/w tips using hypotenuse
                        vol = np.interp(length, [50, 420], [volMin, volMax])
                        volbar = np.interp(length, [50, 700], [700, 150])
                        volper = np.interp(length, [50, 400], [0, 100])
                        print(vol, int(length))
                        volume.SetMasterVolumeLevel(vol, None)

                #cv2.imshow("Image", img)
                if label == 'Right':
                    cv2.circle(img, (x2, y2), 15, (128, 255, 56), cv2.FILLED)  # image #fingers #radius #rgb
                    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # create a line b/w tips of index finger and thumb
                    # Display 'Left Hand'
                    # on left side of window
                    cv2.putText(img, label + ' Hand', (950, 200),cv2.FONT_HERSHEY_PLAIN,2, (0, 255, 0), 2)

                    upCount = 0
                    for coordinate in finger_Coord:
                        if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                            upCount += 1
                    if handList[thumb_Coord[0]][0] < handList[thumb_Coord[1]][0]:
                        upCount += 1
                    cv2.putText(img, f'Finger Count: {str(upCount)}', (540, 90), cv2.FONT_HERSHEY_PLAIN, 2, (133, 15, 59), 4)

                    if (upCount == 2):
                        length1 = hypot(x2 - x1, y2 - y1)  # distance b/w tips using hypotenuse
                    # from numpy we find our length,by converting hand range in terms of volume range ie b/w -63.5 to 0
                        bl = np.interp(length1, [10, 100], [blMin, blMax])
                        blbar = np.interp(length1, [30, 100], [100, 30])
                        blper = np.interp(length1, [10, 100], [0, 100])

                        sbc.set_brightness(bl)

                    if (upCount == 3):
                        zlMin = 0
                        zlMax = 100
                        zlbar = 0; zlper = 0
                        length2 = hypot(x5 - x1, y5 - y1)  # distance b/w tips using hypotenuse
                    # from numpy we find our length,by converting hand range in terms of volume range ie b/w -63.5 to 0
                        zl = np.interp(length2, [10, 100], [zlMin, zlMax])
                        zlbar = np.interp(length2, [30, 100], [100, 30])
                        zlper = np.interp(length2, [10, 100], [0, 100])
                        if(zl > 40 and counting < 10 ):
                            print("zoomed in {}".format(zl))
                            keyboard.press(Key.ctrl)
                            keyboard.press('=')

                            keyboard.release('=')
                            keyboard.release(Key.ctrl)

                        else:
                            print("zoomed out")
                            keyboard.press(Key.ctrl)
                            keyboard.press('-')

                            keyboard.release('-')
                            keyboard.release(Key.ctrl)



        # Hand range 50 - 400
        # Volume range -63.5 - 0.0
        else:
            # Display 'Both Hands' on the image
            cv2.putText(img, 'Both Hands', (500, 50),
                        cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 255, 0), 2)
        # creating volume bar for volume level
        cv2.rectangle(img, (50, 400), (85, 700), (255, 0, 0),
                      4)  # vid ,initial position ,ending position ,rgb ,thickness
        cv2.rectangle(img, (50, int(volbar)), (85, 700), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f"Volume:{int(volper)}%", (10, 350), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
        # tell the volume percentage ,location,font of text,length,rgb color,thickness

        # creating brightness bar for brightness level
       # cv2.rectangle(img, (350, 100), (385, 400), (0, 255, 0),
                  #    4)  # vid ,initial position ,ending position ,rgb ,thickness
        #cv2.rectangle(img, (350, int(blbar)), (385, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f"Brightness:{int(blper)}%", (940, 40), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)
        # tell the volume percentage ,location,font of text,length,rgb color,thickness

    #cv2.imshow('Image', img)  # Show the video
    if (flag == 4):
        cv2.putText(img, f'Swipped right', (20, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        cv2.imshow("Image", img)
    elif (flag == 2):
        cv2.putText(img, f'Swipped left', (950, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        cv2.imshow("Image", img)
    else:
        cv2.imshow("Image", img)

    if timer >= 1.5:
        timer = 0
        counting = False
        direction = "none"
        # =================== cooldown timer ==================
    if cooldown > 0:
        cooldown = cooldown - 1
        # loop delay

    if cv2.waitKey(2) & 0xff == ord('q'):  # By using spacebar delay will stop
        break

cap.release()  # stop cam
cv2.destroyAllWindows()  # close window
