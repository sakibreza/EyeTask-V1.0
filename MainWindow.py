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

        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(10)

    def updateFrame(self):
        img = self.gazeDetector.get_image()
        outImage = toQImage(img)
        outImage = outImage.rgbSwapped()

        self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
        self.main_image_label.setScaledContents(True)

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
