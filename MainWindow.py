from threading import Thread

import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from Speach import Speach
from image_processors.BlinkDetector import BlinkDetector
from image_processors.GazeDetector import GazeDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")
        self.currentFocus = 0
        self.__initialize_buttons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.soundThread = None

        # mode 0 = not controlling wheel chair; controlling menu with eye-blink
        # mode 1 = controling wheel chair with eye-gaze
        # mode 2 = Speech mode
        self.current_mode = 0

        self.cap = cv2.VideoCapture(0)

        self.gazeDetector = GazeDetector()

        self.blinkDetector = BlinkDetector()
        self.initialize_blinkdetector()

        self.speech = Speach()
        self.initialize_speech()

        self.timer.start(10)

        self.main_image_label.setScaledContents(True)

    def updateFrame(self):
        gazeDict = {}
        _, img = self.cap.read()  # numpy.ndarray (480, 640, 3)
        blink_dict = self.blinkDetector.run_blink_detector(img)
        outImage = toQImage(blink_dict["image"])
        outImage = outImage.rgbSwapped()
        self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
        self.updateImageInfo(blink_dict)

        if self.current_mode is 9:
            gazeDict = self.gazeDetector.get_processed_image(img)

        elif self.current_mode is 2:
            if self.soundThread is None or not self.soundThread.is_alive():
                self.soundThread = Thread(target=self.speech.recognize_speech_from_mic)
                self.soundThread.start()
                print("Started Listening")

    def updateImageInfo(self, dict):
        val = "initial = " \
              + str(dict.get("initial")) \
              + "\nCurrent = " \
              + str(dict.get("current")) \
              + "\nDirection = " \
              + str(dict.get("direction")) \
              + "\nAngle = " + str(dict.get("angle")) \
              + "\nBoth Blink = " + str(dict.get("both")) \
              + "\nLeft Blink = " + str(dict.get("left")) \
              + "\nRight Blink = " + str(dict.get("right"))

        self.image_info_textlabel.setText(val)

    def initialize_blinkdetector(self):
        self.blinkDetector.leftAddCallback(self.moveFocusLeft)
        self.blinkDetector.rightAddCallback(self.moveFocusRight)
        self.blinkDetector.bothAddCallback(self.pressFocused)

    def initialize_speech(self):
        self.speech.commands["video"].append(self.moveFocusLeft)
        self.speech.commands["music"].append(self.moveFocusRight)

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
        self.selectMethodComboBox.currentIndexChanged.connect(
            lambda: self.setCurrentMode(self.selectMethodComboBox.currentIndex()))

        self.buttons = [self.b1_1, self.b1_2,
                        self.b1_3, self.b2_1,
                        self.b2_2, self.b2_3,
                        self.b3_1, self.b3_2]
        for b in self.buttons:
            b.setAutoDefault(True)
        self.buttons[self.currentFocus].setFocus(True)

        def playEmail():
            pass

        def playSMS():
            pass

        def controlWheel():
            self.setCurrentMode(9)

        def playFan():
            # TODO: socket programming
            pass

        def playLight():
            # TODO: socket programming
            pass

        def playBrowser():
            import webbrowser
            webbrowser.open_new_tab("http://epaperna.prothomalo.com/")

        def playMusic():
            import os, random, subprocess
            randomfile = random.choice(os.listdir("/home/insaneshadow/Music"))
            file = "/home/insaneshadow/Music/" + randomfile
            subprocess.call(['deepin-music', file])

        def playVideo():
            import os, random, subprocess
            randomfile = random.choice(os.listdir("/home/insaneshadow/Videos"))
            file = "/home/insaneshadow/Videos/" + randomfile
            subprocess.call(['vlc', file])

        self.b1_1.clicked.connect(controlWheel)
        self.b1_2.clicked.connect(playSMS)
        self.b1_3.clicked.connect(playEmail)
        self.b2_1.clicked.connect(playVideo)
        self.b2_2.clicked.connect(playMusic)
        self.b2_3.clicked.connect(playBrowser)
        self.b3_1.clicked.connect(playLight)
        self.b3_2.clicked.connect(playFan)

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

    def pressFocused(self):
        self.buttons[self.currentFocus].animateClick()


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
