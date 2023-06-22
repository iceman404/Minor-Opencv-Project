###################################################################################################################################################################
#  @Author:- John Subba
#  @Title:- Basic Hand Recognition using Mediapipe 
#  @Date:- June-22 2023
###################################################################################################################################################################


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
from pynput.keyboard import Key, Controller
import subprocess

# Initialize video capture
cap = cv2.VideoCapture(1)
x, y = 1920, 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, x)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y)

# Initialize hand detection
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils
finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_Coord = (4, 2)

# Initialize audio volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Initialize variables for volume control
volbar = 700
process1_flag = 4
volper = 0
blbar = 400
blper = 0
volMin, volMax = volume.GetVolumeRange()[:2]
blMin = 10
blMax = 100

# Initialize time and flag variables
ptime = 0
newTime = 0
timer = 0
flag = 0
counting = False
cooldown = 0
direction = "none"
keyboard = Controller()

while True:
    # Read frames from the video capture
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    newTime = time.time()

    # Calculate FPS
    fps = 1 / (newTime - ptime)
    ptime = newTime

    # Perform hand detection
    img.flags.writeable = False
    results = hands.process(imgRGB)
    img.flags.writeable = True

    # Draw lines and text on the image
    cv2.line(img, (400, 0), (400, 728), (255, 0, 255), thickness=2)
    cv2.line(img, (x - 1000, 0), (x - 1000, 728), (255, 0, 255), thickness=2)
    cv2.putText(img, f'timer: {int(timer)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    cv2.putText(img, f'cooldown: {int(cooldown)}', (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

    # Process hand landmarks
    results = hands.process(imgRGB)
    lmList = []
    if results.multi_hand_landmarks:
        handList = []
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                handList.append([id, cx, cy])
            lmList.append(handList)

    # Check for hand landmarks and perform corresponding actions
    if len(lmList) != 0:
        if len(lmList[0]) == 21:
            if direction == "none":
                if lmList[0][thumb_Coord[0]][1] > lmList[0][thumb_Coord[1]][1]:
                    direction = "down"
                else:
                    direction = "up"

            if direction == "up":
                if lmList[0][thumb_Coord[0]][1] < lmList[0][thumb_Coord[1]][1]:
                    direction = "down"
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)

            if direction == "down":
                if lmList[0][thumb_Coord[0]][1] > lmList[0][thumb_Coord[1]][1]:
                    direction = "up"
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)

            dist = hypot(lmList[0][finger_Coord[0][0]][1] - lmList[0][finger_Coord[0][1]][1],
                         lmList[0][finger_Coord[0][0]][2] - lmList[0][finger_Coord[0][1]][2])
            if dist > 50:
                keyboard.press('right')
                keyboard.release('right')

            for id in range(1, 5):
                if lmList[0][finger_Coord[id][0]][2] > lmList[0][finger_Coord[id][1]][2]:
                    keyboard.press('left')
                    keyboard.release('left')
                else:
                    keyboard.press('right')
                    keyboard.release('right')

        elif len(lmList[0]) == 10:
            if direction == "none":
                if lmList[0][thumb_Coord[0]][1] > lmList[0][thumb_Coord[1]][1]:
                    direction = "down"
                else:
                    direction = "up"

            if direction == "up":
                if lmList[0][thumb_Coord[0]][1] < lmList[0][thumb_Coord[1]][1]:
                    direction = "down"
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)

            if direction == "down":
                if lmList[0][thumb_Coord[0]][1] > lmList[0][thumb_Coord[1]][1]:
                    direction = "up"
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)

            dist = hypot(lmList[0][finger_Coord[0][0]][1] - lmList[0][finger_Coord[0][1]][1],
                         lmList[0][finger_Coord[0][0]][2] - lmList[0][finger_Coord[0][1]][2])
            if dist > 50:
                keyboard.press('right')
                keyboard.release('right')

            for id in range(1, 5):
                if lmList[0][finger_Coord[id][0]][2] < lmList[0][finger_Coord[id][1]][2]:
                    keyboard.press('left')
                    keyboard.release('left')
                else:
                    keyboard.press('right')
                    keyboard.release('right')

    # Perform brightness control
    x1 = 400
    x2 = x - 1000
    y1 = 0
    y2 = 728
    newy = np.interp(volper, [volMin, volMax], [y2, y1])
    cv2.line(img, (x1, y1), (x1, y2), (0, 255, 0), 3)
    cv2.line(img, (x1, int(newy)), (x1, y2), (0, 255, 0), cv2.FILLED)
    volper = np.interp(newy, [y2, y1], [volMin, volMax])
    volbar = np.interp(newy, [y2, y1], [400, 150])
    volume.SetMasterVolumeLevel(volper, None)

    # Perform volume control
    newy2 = np.interp(blper, [blMin, blMax], [y2, y1])
    cv2.line(img, (x2, y1), (x2, y2), (0, 255, 0), 3)
    cv2.line(img, (x2, int(newy2)), (x2, y2), (0, 255, 0), cv2.FILLED)
    blper = np.interp(newy2, [y2, y1], [blMin, blMax])
    blbar = np.interp(newy2, [y2, y1], [400, 150])
    sbc.set_brightness(int(blper))

    # Display the FPS on the image
    cv2.putText(img, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the image
    cv2.imshow("Image", img)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()

