import numpy as np

import cv2

import dlib
from imutils import face_utils
from scipy.spatial import distance as dist


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


class BlinkDetector:
    def __init__(self, predictor_dat):

        self.callbacks = {"left": [], "right": [], "both": []}

        # define two constants, one for the eye aspect ratio to indicate
        # blink and then a second constant for the number of consecutive
        # frames the eye must be below the threshold
        self.EYE_AR_THRESH = 0.27
        self.EYE_AR_CONSEC_FRAMES = 5

        # initialize the frame counters and the total number of blinks
        self.BOTH_COUNTER = 0
        self.COUNTER_L = 0
        self.COUNTER_R = 0
        self.TOTAL = 0
        self.TOTAL_L = 0
        self.TOTAL_R = 0

        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        print("BlinkDetector :[INFO] loading facial landmark predictor...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_dat)

        # grab the indexes of the facial landmarks for the left and
        # right eye, respectively
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    def run_blink_detector(self, frame):
        retDict = {"eyegaze": None}

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
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # get the eye frame for the window

            eyegaze = frame[max(leftEye[1][1], 0):leftEye[5][1], max(leftEye[0][0], 0):leftEye[3][0]]
            # eyegaze = cv2.resize(eyegaze, (640, 450))
            eyegaze = cv2.resize(eyegaze, (0, 0), fx=8, fy=8)
            retDict["eyegaze"] = np.copy(eyegaze)

            # TODO: same for both

            # both
            if leftEAR < self.EYE_AR_THRESH - 0.02 and rightEAR < self.EYE_AR_THRESH - 0.02:
                self.BOTH_COUNTER += 1
            else:
                self.BOTH_COUNTER = 0
            # left
            if leftEAR < self.EYE_AR_THRESH:
                self.COUNTER_L += 1
            else:
                self.COUNTER_L = 0
            # right
            if rightEAR < self.EYE_AR_THRESH:
                self.COUNTER_R += 1
            else:
                self.COUNTER_R = 0

            # if the eyes were closed for a sufficient number of
            # then increment the total number of blinks
            if self.BOTH_COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                self.TOTAL += 1
                self.COUNTER_R = 0
                self.COUNTER_L = 0
                self.BOTH_COUNTER = 0
                for func in self.callbacks["both"]:
                    func()

            if self.COUNTER_L >= self.EYE_AR_CONSEC_FRAMES:
                self.TOTAL_L += 1
                self.COUNTER_L = 0
                self.COUNTER_R = 0
                self.BOTH_COUNTER = 0
                for func in self.callbacks["left"]:
                    func()

            if self.COUNTER_R >= self.EYE_AR_CONSEC_FRAMES:
                self.TOTAL_R += 1
                self.COUNTER_L = 0
                self.COUNTER_R = 0
                self.BOTH_COUNTER = 0
                for func in self.callbacks["right"]:
                    func()

            self.draw_in_frame(frame, ear, leftEAR, rightEAR, leftEye, rightEye)
        retDict["image"] = frame
        return retDict

    def draw_in_frame(self, frame, ear, leftEAR, rightEAR, leftEye, rightEye):
        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)

        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # draw the total number of blinks on the frame along with
        # the computed eye aspect ratio for the frame
        cv2.putText(frame, "Both Blinks: {}".format(self.TOTAL), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "Left Blinks: {}".format(self.TOTAL_L), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "Right Blinks: {}".format(self.TOTAL_R), (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "L-EAR: {:.2f}".format(leftEAR), (10, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "R-EAR: {:.2f}".format(rightEAR), (300, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    def leftAddCallback(self, callbacks=None):
        self.callbacks["left"].append(callbacks)

    def rightAddCallback(self, callbacks=None):
        self.callbacks["right"].append(callbacks)

    def bothAddCallback(self, callbacks=None):
        self.callbacks["both"].append(callbacks)
