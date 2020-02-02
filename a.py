import cv2
import numpy as np
import os
import face_recognition
import time
from gpiozero import Buzzer
from gpiozero import LED
import RPi.GPIO as GPIO
from time import sleep

buzzer = Buzzer(15)
red = LED(23)
green = LED(24)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
url = "http://" + '192.168.43.102:8080' + "/video"

known_faces = []
known_names = []
print('here')
images_path = 'Face_Images'
for image in os.listdir(images_path):
    image_loaded = face_recognition.load_image_file(images_path + '/' + image)
    print(image.split('.')[0])
    face_encoding = face_recognition.face_encodings(image_loaded)[0]
    known_faces.append(face_encoding)
    known_names.append(image.split('.')[0])
print(known_names)
face_locations = []
face_encodings = []
face_names = []
font = cv2.FONT_HERSHEY_DUPLEX
cap = cv2.VideoCapture(url)
flag = 0
ask_for_name_flag = False
open_flag = False
while True:

    ret, frame = cap.read()
    if flag and time.time() - before_time < 3:
        frame = before_frame
        ask_for_name_flag = True
    elif not open_flag and ask_for_name_flag and len(face_encodings) == 1:
        print("please enter your name to add to faces or b to ignore: ")
        inp = raw_input()
        if inp != "b":
            print("You have been added to list " + inp)
            known_names.append(inp)
            known_faces.append(face_encodings[0])
            ret, frame = cap.read()
            cv2.imwrite(images_path + '/' + inp + '.jpg', capture_frame)
        ask_for_name_flag = False
        open_flag = False
        flag = 0
    elif open_flag:
        print('Welcome home:))')
        open_flag = False
        ask_for_name_flag = False
        flag = 0

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_names = []

    input_state = GPIO.input(18)
    if not input_state:
        asadi = 0
        ret, capture_frame = cap.read()
        while asadi in range(20):
            buzzer.on()
            sleep(0.01)
            buzzer.off()
            sleep(0.01)
            asadi += 1
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        open_flag = False
        for face_encoding in face_encodings:
            match = face_recognition.compare_faces(np.array(known_faces), face_encoding)
            name = "Unknown"

            for i in range(len(match)):

                if match[i]:
                    name = known_names[i]
                    open_flag = True
                    break

            face_names.append(name)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            r = 0
            g = 255
            if name == 'Unknown':
                r = 255
                g = 0
            cv2.rectangle(frame, (left, top), (right, bottom), (0, g, r), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, g, r), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        flag = 1
        before_time = time.time()
        before_frame = frame

    cv2.imshow('face recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
