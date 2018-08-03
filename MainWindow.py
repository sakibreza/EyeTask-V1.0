from threading import Thread

import cv2
import smtplib

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from Speach import Speach
from WheelChair import WheelChair
from image_processors.BlinkDetector import BlinkDetector
from image_processors.GazeDetector import GazeDetector


from zeep import Client

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./ui/MainWindow.ui", self)
        self.setWindowTitle("Eye Gaze Detection")
        self.resetButton.clicked.connect(self.resetAll)

        self.currentFocus = 0
        self.__initialize_buttons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.soundThread = None

        self.chair = WheelChair()

        self.current_subprecess = None

        # mode 0 = not controlling wheel chair; controlling menu with eye-blink
        # mode 1 = controling wheel chair with eye-gaze and eye-blink
        # mode 2 = Speech mode
        # mode 3 = Speech mode for wheel chair
        self.current_mode = 0

        self.cap = cv2.VideoCapture(1)

        self.gazeDetector = GazeDetector()

        self.blinkDetector = BlinkDetector()
        self.initialize_blinkdetector()

        # self.speech = Speach()
        # self.initialize_speech()

        self.timer.start(10)

        self.main_image_label.setScaledContents(True)

    def resetAll(self):
        self.current_mode = 0
        self.chair.stop()
        self.chair.is_going = False
        self.gazeDetector.reset()
        self.blinkDetector.reset()

    def updateFrame(self):
        info = {}

        if self.current_mode == 0 or self.current_mode == 1:
            _, img = self.cap.read()
            blink_dict = self.blinkDetector.run_blink_detector(img)
            outImage = toQImage(blink_dict["image"])
            outImage = outImage.rgbSwapped()
            self.main_image_label.setPixmap(QPixmap.fromImage(outImage))
            info["left"] = blink_dict["leftTotal"]
            info["right"] = blink_dict["rightTotal"]
            info["both"] = blink_dict["bothTotal"]

            if blink_dict["both"]:
                if self.current_subprecess is not None:
                    self.current_subprecess.terminate()
                    self.current_subprecess = None

            if self.current_subprecess is not None:
                return

            if self.current_mode is 1:
                gazeDict = self.gazeDetector.get_processed_image(img)
                info["rightEAR"] = gazeDict["rightEAR"]
                info["leftEAR"] = gazeDict["leftEAR"]
                info["dir"] = gazeDict["direction"]
                if gazeDict["direction"] == "left":
                    self.chair.left()
                if gazeDict["direction"] == "right":
                    self.chair.right()
                if gazeDict["direction"] == "center":
                    self.chair.start()

                if blink_dict["left"] or blink_dict["right"]:
                    self.chair.toggleStartStop()

                elif blink_dict["both"]:
                    self.chair.stop()
                    self.chair.is_going = False
                    self.current_mode = 0
                    self.gazeDetector.closeAll()

        elif self.current_mode == 2:
            if self.soundThread is None or not self.soundThread.is_alive():
                self.soundThread = Thread(target=self.speech.recognize_speech_from_mic)
                self.soundThread.start()
                print("Started Listening")

        self.updateImageInfo(info)

    def updateImageInfo(self, dict):
        val = ""
        for key, value in dict.items():
            val = val + "\n" + str(key) + " : " + str(value)

        self.image_info_textlabel.setText(val)

    def initialize_blinkdetector(self):
        self.blinkDetector.leftAddCallback(self.moveFocusLeft)
        self.blinkDetector.rightAddCallback(self.moveFocusRight)
        self.blinkDetector.bothAddCallback(self.pressFocused)

    def initialize_speech(self):
        self.speech.commands["video"].append(self.playVideo)
        self.speech.commands["music"].append(self.playMusic)
        self.speech.commands["SMS"].append(self.playSMS)
        self.speech.commands["message"].append(self.playEmail)
        self.speech.commands["light"].append(self.playLight)
        self.speech.commands["fan"].append(self.playFan)
        self.speech.commands["news"].append(self.playBrowser)

        self.speech.commands["start"].append(self.chair.start)
        self.speech.commands["stop"].append(self.chair.stop)
        self.speech.commands["right"].append(self.chair.right)
        self.speech.commands["left"].append(self.chair.left)

        self.speech.commands["close"].append(self.stopCurrentSubprocess)

    def stopCurrentSubprocess(self):
        if self.current_subprecess is not None:
            self.current_subprecess.terminate()

    def setCurrentMode(self, i):
        self.current_mode = i

    def comboboxIndexChanged(self):
        if self.selectMethodComboBox.currentIndex() == 0:
            self.current_mode = 0
        elif self.selectMethodComboBox.currentIndex() == 1:
            pass
        elif self.selectMethodComboBox.currentIndex() == 2:
            self.current_mode = 2
        if self.selectMethodComboBox.currentIndex() != 2:
            self.soundThread = None

    def __initialize_buttons(self):
        self.selectMethodComboBox.clear()
        self.selectMethodComboBox.addItems([
            "Eye-Help",
            "Head-Help",
            "Voice-Help"
        ])
        self.selectMethodComboBox.setCurrentIndex(0)
        self.selectMethodComboBox.currentIndexChanged.connect(self.comboboxIndexChanged)

        self.buttons = [self.b1_1, self.b1_2,
                        self.b1_3, self.b2_1,
                        self.b2_2, self.b2_3,
                        self.b3_1, self.b3_2]
        for b in self.buttons:
            b.setAutoDefault(True)
        self.buttons[self.currentFocus].setFocus(True)

        def playEmail():
            try:
                fromaddr = 'eyegaze.kuet@gmail.com'
                toaddr = 'sakibreza1@gmail.com'
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = 'Doctor Appointment'
                 
                body = 'I am facing problem.Please come to see me if you are free.'
                msg.attach(MIMEText(body, 'plain'))
                 
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(fromaddr, '060701cse')
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
                print('Email Sent Successfully')
            except:    
                print('Email not sent')
        self.b1_1.clicked.connect(self.controlWheel)
        self.b1_2.clicked.connect(self.playSMS)
        self.b1_3.clicked.connect(self.playEmail)
        self.b2_1.clicked.connect(self.playVideo)
        self.b2_2.clicked.connect(self.playMusic)
        self.b2_3.clicked.connect(self.playBrowser)
        self.b3_1.clicked.connect(self.playLight)
        self.b3_2.clicked.connect(self.playFan)


        def playSMS():
            try:
                url = 'https://api2.onnorokomsms.com/sendsms.asmx?WSDL' 
                client = Client(url) 
                userName = '01516111574' 
                password = '54124' 
                recipientNumber = '01521323429' 
                smsText = 'Hello Eygaze' 
                smsType = 'TEXT' 
                maskName = '' 
                campaignName = '' 
                client.service.OneToOne(userName,password,recipientNumber,smsText,smsType,maskName,campaignName)
                print('SMS sent!')
            except:
                print('SMS nor sent!')
        def controlWheel():
            self.setCurrentMode(9)

    def controlWheel(self):
        self.setCurrentMode(9)

    def playFan(self):
        self.chair.playFan()

    def playLight(self):
        self.chair.playLight()

    def playBrowser(self):
        import webbrowser
        webbrowser.open_new_tab("http://epaperna.prothomalo.com/")

    def playMusic(self):
        import os, random, subprocess
        randomfile = random.choice(os.listdir("/home/insaneshadow/Music"))
        file = "/home/insaneshadow/Music/" + randomfile
        self.current_subprecess = subprocess.Popen(['deepin-music', file])

    def playVideo(self):
        import os, random, subprocess
        randomfile = random.choice(os.listdir("/home/insaneshadow/Videos"))
        file = "/home/insaneshadow/Videos/" + randomfile
        self.current_subprecess = subprocess.Popen(['vlc', file])

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
