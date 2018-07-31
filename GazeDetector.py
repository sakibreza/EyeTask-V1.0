import cv2
import numpy as np


class GazeDetector:
    def __init__(self, cascade):
        self.pupil_cascade = cv2.CascadeClassifier(cascade)

        self.cap = cv2.VideoCapture(0)
        self.init = [0, 0]
        self.coordinate = [0, 0]
        self.radius = 5

    def get_image(self):
        _, img = self.cap.read()  # numpy.ndarray (480, 640, 3)
        # img = cv2.flip(img, -1)
        # img = cv2.flip(img, +1)

        img = img[200:500, 300:500, :]  # numpy.ndarray (280, 340, 3)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pupil = self.pupil_cascade.detectMultiScale(gray, 1.3, 4)
        cv2.circle(img, (self.init[0], self.init[1]), self.radius, (0, 255, 0), 2)
        cv2.line(img, (self.init[0], self.init[1]), (self.coordinate[0], self.coordinate[1]), (0, 255, 0), 2)

        if pupil is not ():
            x, y, w, h = pupil[0][0], pupil[0][1], pupil[0][2], pupil[0][3]

            self.coordinate = [int(x + w / 2), int(y + h / 2)]
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

            # print("-----")
            # print("initial = " + str(self.init))
            # print("current = " + str(self.coordinate))
            # print("direction = " + self.direction())
            # print("angle = " + self.getangle())

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfTextr = (200, 250)
            bottomLeftCornerOfTextc = (80, 250)
            bottomLeftCornerOfTextl = (20, 250)
            fontScale = 1
            fontColor = (255, 255, 255)
            lineType = 2

            if dir == "center":
                img = cv2.putText(img, '< Center >',
                                  bottomLeftCornerOfTextc,
                                  font,
                                  fontScale,
                                  fontColor,
                                  lineType)
            elif dir == "right":
                img = cv2.putText(img, 'Right >',
                                  bottomLeftCornerOfTextr,
                                  font,
                                  fontScale,
                                  fontColor,
                                  lineType)

            elif dir == "left":
                img = cv2.putText(img, '< left',
                                  bottomLeftCornerOfTextl,
                                  font,
                                  fontScale,
                                  fontColor,
                                  lineType)

        ret = {"image": img, "initial": self.init, "current": self.coordinate, "direction": self.direction(),
               "angle": self.getangle()}

        return ret

    def direction(self):
        ix = self.init[0]
        cx = self.coordinate[0]
        if self.init == [0, 0]:
            return "not initialized"
        elif ix + self.radius >= cx >= ix - self.radius:
            return "center"
        elif cx >= ix + self.radius:
            return "right"
        elif cx <= ix - self.radius:
            return "left"

    def getangle(self):
        ix = self.init[0]
        iy = self.init[1]
        cx = self.coordinate[0]
        cy = self.coordinate[1]
        cur = np.array([cx, cy])
        init = np.array([ix, iy])
        c = np.array([1000, iy])
        init_cur = cur - init
        init_c = c - init
        cosine_angle = np.dot(init_cur, init_c) / (np.linalg.norm(init_cur) * np.linalg.norm(init_c))
        angle = np.arccos(cosine_angle)
        return str(np.degrees(angle))
