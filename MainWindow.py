from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from GazeDetector import GazeDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")
        self.upload_haar_button.clicked.connect(self.selectHaar)
        self.haar_file_location_lineEdit.setText("haar_cascades/cascade_eye.xml")

        self.gazeDetector = GazeDetector(self.haar_file_location_lineEdit.text())
        self.timer = QTimer(self)

        self.currentFocus = 0
        self.buttons = [self.b1_1, self.b1_2, self.b1_3,
                        self.b2_1, self.b2_2, self.b2_3,
                        self.b3_1, self.b3_2, self.b3_3]
        for b in self.buttons:
            b.setAutoDefault(True)

        self.buttons[self.currentFocus].setFocus(True)

        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(10)

    def moveFocusRight(self):
        self.currentFocus = (self.currentFocus + 1) % 8
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusLeft(self):
        self.currentFocus = (self.currentFocus - 1) % 8
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusUp(self):
        self.currentFocus = (self.currentFocus + 3) % 8
        self.buttons[self.currentFocus].setFocus(True)

    def moveFocusDown(self):
        self.currentFocus = (self.currentFocus - 3) % 8
        self.buttons[self.currentFocus].setFocus(True)

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

    def updateFrame(self):
        getDict = self.gazeDetector.get_image()
        self.updateImage(getDict["image"])
        self.updateImageInfo(getDict)

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
