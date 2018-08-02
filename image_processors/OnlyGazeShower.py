# USAGE
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat --video blink_detection_demo.mp4
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat

import time

import cv2
import dlib
import numpy as np
from imutils import face_utils
# import the necessary packages
from scipy.spatial import distance as dist


class OnlyGazeShower:

    def __init__(self):
        self.con_frame = 2
        self.dir_c = 0
        self.dir_l = 0
        self.dir_r = 0
        self.init = [0, 0]
        self.coordinate = [0, 0]
        self.eye_cascade = cv2.CascadeClassifier('haar_cascades/cascade.xml')
        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("haar_cascades/shape_predictor_68_face_landmarks.dat")

        # grab the indexes of the facial landmarks for the left and
        # right eye, respectively
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        # cap = cv2.VideoCapture(0)
        # start the video stream thread
        # print("[INFO] starting video stream thread...")
        # time.sleep(1.0)

        # loop over frames from the video stream
    # while True:
    # if this is a file video stream, then we need to check if
    # there any more frames left in the buffer to process
    # TODO: get the frame
    # _, frame = cap.read()
    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale
    # channels)
    # print(type(frame))

    def direction(self, ini, cur):
        ix = ini[0]
        iy = ini[1]
        cx = cur[0]
        cy = cur[1]
        rad = 30
        if self.init == [0, 0]:
            return "not initialized"
        elif ix + rad >= cx >= ix - rad:
            return "center"
        elif cx >= ix + rad:
            return "right"
        elif cx <= ix - rad:
            return "left"

    def getangle(self, ini, cur):
        ix = ini[0]
        iy = ini[1]
        cx = cur[0]
        cy = cur[1]
        a = np.array([cx, cy])
        b = np.array([ix, iy])
        c = np.array([1000, iy])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return str(np.degrees(angle))

    def eye_aspect_ratio(self, eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-self.coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-self.coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear

    def run(self, frame):

        frame = cv2.resize(frame, (640, 450))
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = self.detector(gray, 0)

        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[self.rStart:self.rEnd]
            rightEye = shape[self.lStart:self.lEnd]
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0
            # compute the convex hull for the left and right eye, then
            # visualize each of the eyes
            # TODO: ^^^ same for both

            frame = frame[max(leftEye[1][1], 0):leftEye[5][1], max(leftEye[0][0], 0):leftEye[3][0]]
            frame = cv2.resize(frame, (0, 0), fx=8, fy=8)
            self.init[0] = int(frame.shape[1] / 2)
            self.init[1] = int(frame.shape[0] / 2)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        img = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=2)
        # Finding unknown region
        eye = self.eye_cascade.detectMultiScale(img, 1.1, 5)
        cv2.circle(img, (self.init[0], self.init[1]), 3, (255, 0, 0), -1)
        cv2.line(img, (self.init[0] - 20, self.init[1]), (self.init[0] + 20, self.init[1]), (255, 0, 0), 2)
        cv2.line(img, (self.init[0], self.init[1] - 20), (self.init[0], self.init[1] + 20), (255, 0, 0), 2)
        cv2.circle(img, (self.coordinate[0], self.coordinate[1]), 3, (255, 0, 0), -1)
        # cv2.line(img, (self.init[0], self.init[1]), (self.coordinate[0],self.coordinate[1]), (0,255,0), 2)
        for (x, y, w, h) in eye:
            # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            self.coordinate = [int(x + w / 2), int(y + h / 2)]
            print("-----")
            print("initial = " + str(self.init))
            print("current = " + str(self.coordinate))
            dir = self.direction(self.init, self.coordinate)
            print("direction = " + dir)
            angle = self.getangle(self.init, self.coordinate)
            print("angle = " + angle)

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfTextr = (20, 30)
            bottomLeftCornerOfTextc = (20, 30)
            bottomLeftCornerOfTextl = (20, 30)
            fontScale = 1
            fontColor = (255, 255, 255)
            lineType = 2

            if dir == "center":

                self.dir_c += 1

                if self.dir_c > self.con_frame:
                    self.dir_l = 0
                    self.dir_r = 0
                    img = cv2.putText(img, '< Center >',
                                      bottomLeftCornerOfTextc,
                                      font,
                                      fontScale,
                                      fontColor,
                                      lineType)


            elif dir == "right":
                self.dir_r += 1

                if self.dir_r > self.con_frame:
                    self.dir_l = 0
                    self.dir_c = 0
                    img = cv2.putText(img, 'Right >',
                                      bottomLeftCornerOfTextc,
                                      font,
                                      fontScale,
                                      fontColor,
                                      lineType)

            elif dir == "left":
                self.dir_l += 1

                if self.dir_l > self.con_frame:
                    self.dir_c = 0
                    self.dir_r = 0
                    img = cv2.putText(img, '< Left',
                                      bottomLeftCornerOfTextc,
                                      font,
                                      fontScale,
                                      fontColor,
                                      lineType)

            cv2.imshow('eye_gaze', img)
            # cv2.imshow('eye_blink', blink_frame)

            # k = cv2.waitKey(30) & 0xff
            # if k == 27:
            #     break
