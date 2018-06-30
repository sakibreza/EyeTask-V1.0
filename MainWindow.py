from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import numpy as np
import cv2

class GazeDetector:
    def __init__(self, cascade):
        self.face_cascade = cv2.CascadeClassifier(cascade)

        self.cap = cv2.VideoCapture(0)
        self.init = [0, 0]
        self.coordinate = [0, 0]


        # while 1:
        #     getImage()
        #     k = cv2.waitKey(30) & 0xff
        #     if k == 105:
        #         init = [int(x + w / 2), int(y + h / 2)]
        #     elif k == 27:
        #         break

        # cap.release()
        # cv2.destroyAllWindows()

    def getImage(self):
        ret, img = self.cap.read()
        img = cv2.flip(img, -1)
        img = cv2.flip(img, +1)
        return img
        print(type(img))
        print(img.shape)
        img = img[200:500, 300:5000, :]
        print(type(img))
        print(img.shape)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 4)
        cv2.circle(img, (self.init[0], self.init[1]), 3, (0, 255, 0), -1)
        cv2.line(img, (self.init[0], self.init[1]), (self.coordinate[0], self.coordinate[1]), (0, 255, 0), 2)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            coordinate = [int(x + w / 2), int(y + h / 2)]
            print("-----")
            print("initial = " + str(self.init))
            print("current = " + str(coordinate))
            dir = self.direction()
            print("direction = " + dir)
            angle = self.getangle()
            print("angle = " + angle)

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

        # cv2.imshow('img', img)
        return img


    def direction(self):
        ix = self.init[0]
        cx = self.coordinate[0]
        rad = 5
        if self.init == [0, 0]:
            return "not initialized"
        elif ix + rad >= cx >= ix - rad:
            return "center"
        elif cx >= ix + rad:
            return "right"
        elif cx <= ix - rad:
            return "left"


    def getangle(self):
        ix = self.init[0]
        iy = self.init[1]
        cx = self.coordinate[0]
        cy = self.coordinate[1]
        a = np.array([cx, cy])
        b = np.array([ix, iy])
        c = np.array([1000, iy])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return str(np.degrees(angle))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")
        self.upload_haar_button.clicked.connect(self.selectHaar)
        self.haar_file_location_lineEdit.setText("haar_cascades/cascade_eye.xml")
        self.gazeDetector = GazeDetector(self.haar_file_location_lineEdit.text())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.start_button.clicked.connect(self.startButtonClick)
        # self.timer.start(5)


    def startButtonClick(self):
        self.timer.start(5)


    def updateFrame(self):
        img = self.gazeDetector.getImage()
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
        self.main_image_label.setScaledContents(True)

    def selectHaar(self):
        file = QFileDialog.getOpenFileName()
        self.haar_file_location_lineEdit.setText(file[0])
        self.gazeDetector.face_cascade = file[0]

    def addShortcutDialog(self):
        addShortcut = QDialog(self)
        loadUi("./ui/AddShortcutDialog.ui", addShortcut)
        addShortcut.exec_()
