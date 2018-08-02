import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from image_processors.BlinkDetector import BlinkDetector
from image_processors.GazeDetector import GazeDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")
        self.upload_haar_button.clicked.connect(self.selectHaar)
        self.haar_file_location_lineEdit.setText("haar_cascades/cascade_eye.xml")

        # mode 0 = not controlling wheel chair; controlling menu with eye-blink
        # mode 1 = controling wheel chair with eye-gaze
        self.current_mode = 1

        self.cap = cv2.VideoCapture(1)
        self.gazeDetector = GazeDetector(self.haar_file_location_lineEdit.text())

        # TODO: make a way to select the .dat file
        self.blinkDetector = BlinkDetector("haar_cascades/shape_predictor_68_face_landmarks.dat")
        self.blinkDetector.leftAddCallback(self.moveFocusLeft)
        self.blinkDetector.rightAddCallback(self.moveFocusRight)
        self.blinkDetector.bothAddCallback(self.pressFocused)

        self.currentFocus = 0
        self.__initialize_buttons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(10)

    def updateFrame(self):

        _, img = self.cap.read()  # numpy.ndarray (480, 640, 3)
        blink_dict = {}
        if self.current_mode is 0:
            blink_dict = self.blinkDetector.run_blink_detector(img)
            outImage = toQImage(blink_dict["image"])
            outImage = outImage.rgbSwapped()
            self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
            self.main_image_label.setScaledContents(True)

        elif self.current_mode is 1:
            blink_dict = self.blinkDetector.run_blink_detector(img)
            if blink_dict["eyegaze"] is not None:
                gazeDict = self.gazeDetector.get_processed_image(blink_dict["eyegaze"])
                self.updateImageInfo(gazeDict)

        if blink_dict["eyegaze"] is not None:
            self.updateImage(gazeDict["image"])
        else:
            self.updateImage(blink_dict["image"])
        # self.updateImage(blink_dict["image"])

    def __initialize_buttons(self):
        self.buttons = [self.b1_1, self.b1_2, self.b1_3,
                        self.b2_1, self.b2_2, self.b2_3,
                        self.b3_1, self.b3_2, self.b3_3]
        for b in self.buttons:
            b.setAutoDefault(True)
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusRight(self):
        self.currentFocus = (self.currentFocus + 1) % 9
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusLeft(self):
        self.currentFocus = (self.currentFocus - 1) % 9
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusUp(self):
        self.currentFocus = (self.currentFocus + 3) % 9
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusDown(self):
        self.currentFocus = (self.currentFocus - 3) % 9
        self.buttons[self.currentFocus].setFocus(True)

    def pressFocused(self):
        self.buttons[self.currentFocus].animateClick()

    def updateImage(self, img):
        outImage = toQImage(img)
        outImage = outImage.rgbSwapped()
        self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
        self.main_image_label.setScaledContents(True)

    def updateImageInfo(self, dict):
        val = "initial = " \
              + str(dict["initial"]) \
              + "\nCurrent = " \
              + str(dict["current"]) \
              + "\nDirection = " \
              + str(dict["direction"]) \
              + "\nAngle = " + str(dict["angle"])

        self.image_info_textlabel.setText(val)

    def selectHaar(self):
        file = QFileDialog.getOpenFileName()
        self.haar_file_location_lineEdit.setText(file[0])
        self.gazeDetector.pupil_cascade = file[0]


def toQImage(raw_img):
    from numpy import copy
    img = copy(raw_img)
    qformat = QImage.Format_Indexed8
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888

    outImg = QImage(img.tobytes(), img.shape[1], img.shape[0], img.strides[0], qformat)
    return outImg
