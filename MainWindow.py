from threading import Thread

import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from Speach import Speach
from image_processors.BlinkDetector import BlinkDetector
from image_processors.OnlyGazeShower import OnlyGazeShower


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")

        # mode 0 = not controlling wheel chair; controlling menu with eye-blink
        # mode 1 = controling wheel chair with eye-gaze
        # mode 2 = Speech mode
        self.current_mode = 0

        self.cap = None
        if self.current_mode is 0 or 1:
            self.cap = cv2.VideoCapture(0)
        # self.gazeDetector = GazeDetector(self.haar_file_location_lineEdit.text())
        self.gazeDetector = OnlyGazeShower()

        self.blinkDetector = BlinkDetector("haar_cascades/shape_predictor_68_face_landmarks.dat")
        self.blinkDetector.leftAddCallback(self.moveFocusLeft)
        self.blinkDetector.rightAddCallback(self.moveFocusRight)
        self.blinkDetector.bothAddCallback(self.pressFocused)

        self.speech = Speach()
        self.speechObj()

        self.currentFocus = 0
        self.__initialize_buttons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(10)

        self.thread = None
        self.main_image_label.setScaledContents(True)

    def speechObj(self):
        self.speech.commands["video"].append(self.moveFocusLeft)
        self.speech.commands["music"].append(self.moveFocusRight)

    def updateFrame(self):
        gazeDict = {}
        _, img = self.cap.read()  # numpy.ndarray (480, 640, 3)
        blink_dict = self.blinkDetector.run_blink_detector(img)
        outImage = toQImage(blink_dict["image"])
        outImage = outImage.rgbSwapped()
        self.main_image_label.setPixmap(QPixmap.fromImage(outImage))

        if self.current_mode is 1:
            self.gazeDetector.run(img)

        elif self.current_mode is 2:
            if self.thread is None or not self.thread.is_alive():
                self.thread = Thread(target=self.speech.recognize_speech_from_mic)
                # self.speech.recognize_speech_from_mic()
                self.thread.start()
                print("thread started")

    def setCurrentMode(self, i):
        self.current_mode = i

    def __initialize_buttons(self):
        self.selectMethodComboBox.clear()
        self.selectMethodComboBox.addItems([
            "Eye-Help",
            "Head-Help",
            "Voice-Help"
        ])
        self.selectMethodComboBox.setCurrentIndex(0)
        self.selectMethodComboBox.currentIndexChanged.connect(lambda: self.setCurrentMode(self.selectMethodComboBox.currentIndex()))



        self.buttons = [self.b1_1, self.b1_2, self.b1_3,
                        self.b2_1, self.b2_2, self.b2_3,
                        self.b3_1, self.b3_2, self.b3_3]
        for b in self.buttons:
            b.setAutoDefault(True)
        self.buttons[self.currentFocus].setFocus(True)

        self.b1_1.clicked.connect(self.controlWheel)
        self.b1_2.clicked.connect(self.playSMS)
        self.b1_3.clicked.connect(self.playEmail)
        self.b2_1.clicked.connect(self.playVideo)
        self.b2_2.clicked.connect(self.playMusic)
        self.b2_3.clicked.connect(self.playBrowser)
        self.b3_1.clicked.connect(self.playLight)
        self.b3_2.clicked.connect(self.playFan)
        self.b3_3.clicked.connect(self.playEmergency)

    def playEmail(self):
        pass

    def playSMS(self):
        pass

    def controlWheel(self):
        pass

    def playEmergency(self):
        # TODO: socket programming
        pass

    def playFan(self):
        # TODO: socket programming
        pass

    def playLight(self):
        # TODO: socket programming
        pass

    def playBrowser(self):
        import webbrowser
        webbrowser.open_new_tab("http://epaperna.prothomalo.com/")

    def playMusic(self):
        import os, random, subprocess
        randomfile = random.choice(os.listdir("/home/insaneshadow/Music"))
        file = "/home/insaneshadow/Music/" + randomfile
        subprocess.call(['deepin-music', file])

    def playVideo(self):
        import os, random, subprocess
        randomfile = random.choice(os.listdir("/home/insaneshadow/Videos"))
        file = "/home/insaneshadow/Videos/" + randomfile
        subprocess.call(['vlc', file])


    def blinkModeOn(self):
        self.current_mode = 0

    def eyegazeModeOn(self):
        self.current_mode = 1

    def soundModeOn(self):
        self.current_mode = 2

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
