import cv2
import numpy as np


class GazeDetector:
    def __init__(self, cascade):
        self.pupil_cascade = cv2.CascadeClassifier(cascade)

        self.init = [0, 0]
        self.coordinate = [0, 0]
        self.radius = 5

        self.CONSEC_FRAMES = 2
        self.dir_c = 0
        self.dir_l = 0
        self.dir_r = 0

    def draw_in_frame(self, img):
        cv2.line(img, (self.init[0] - 15, self.init[1] - 15), (self.init[0] + 15, self.init[1] + 15), (255, 0, 0), 2)
        cv2.line(img, (self.init[0] + 15, self.init[1] - 15), (self.init[0] - 15, self.init[1] + 15), (255, 0, 0), 2)
        cv2.circle(img, (self.coordinate[0], self.coordinate[1]), 3, (255, 0, 0), 2)
        # cv2.line(img, (init[0], init[1]), (coordinate[0],coordinate[1]), (0,255,0), 2)

    def get_processed_image(self, img):

        self.init[0] = img.shape[1] // 2
        self.init[1] = img.shape[0] // 2

        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=2)

        # Finding unknown region
        eye = self.pupil_cascade.detectMultiScale(img, 1.1, 5)

        self.draw_in_frame(img)

        for (x, y, w, h) in eye:
            self.coordinate = [(x + w) // 2, (y + h) // 2]
            print("-----")
            print("initial = " + str(self.init))
            print("current = " + str(self.coordinate))
            dir = self.direction()
            print("direction = " + dir)
            angle = self.getangle()
            print("angle = " + angle)

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfTextc = (20, 30)
            fontScale = 1
            fontColor = (255, 255, 255)
            lineType = 2

            if dir == "center":

                self.dir_c += 1

                if self.dir_c > self.CONSEC_FRAMES:
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

                if self.dir_r > self.CONSEC_FRAMES:
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

                if self.dir_l > self.CONSEC_FRAMES:
                    self.dir_c = 0
                    self.dir_r = 0
                    img = cv2.putText(img, '< Left',
                                      bottomLeftCornerOfTextc,
                                      font,
                                      fontScale,
                                      fontColor,
                                      lineType)

        # cv2.imshow("eye-gaze", img)
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
