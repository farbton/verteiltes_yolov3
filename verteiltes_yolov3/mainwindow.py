import sys
import cv2
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore

from reader import Reader
from yolo import Yolo

#Klasse die in das MainWindow schreiben darf
class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Viewer for Yolov3")
        self.reader = Reader(self)
        self.yolo = Yolo(self)
        self.lock = True
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def start(self):        
        self.refresh_button.clicked.connect(self.label_write)
        self.actionload_image.triggered.connect(self.loadImage)
        self.actionload_video.triggered.connect(self.loadVideo)
        self.pushButtonStartDetection.clicked.connect(self.startDetection)

    def startDetection(self):
        print("startDetection")
        self.statusBar().showMessage("detection ... ")
        self.console.setText(self.console.text() + "start detection ... " + str(self.scrollArea.verticalScrollBar().maximum()) + "\n")
        self.console.repaint()
        #self.autoscroll()
        self.detectImage()

    def detectImage(self):
        self.detectedImage = self.yolo.detectImage()
        self.convertCv2ToQImage()
        #cv2.imshow("test", self.detectedImage)
        self.setPlayerHeightWidth()
        self.qimageToPixmap()
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        self.statusBar().clearMessage()
        self.console.setText(self.console.text() + "ready ... \n")
        self.console.repaint()
        self.autoscroll()
        self.lock = False

    def label_write(self):
        self.label.setText("hallo")
     
    def setPlayerHeightWidth(self):
        self.playerHeight = self.player.geometry().height()
        self.playerWidth = self.player.geometry().width()

    def convertCv2ToQImage(self):
        self.qimage = QImage(self.detectedImage, 512, 512, QImage.Format_BGR888)

    def qimageToPixmap(self):
        self.pixMap = QPixmap(self.qimage)

    def resizePixmap(self):
        self.pixMap = self.pixMap.scaled(QtCore.QSize(self.playerHeight, self.playerWidth), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
    
    def pixmapSetScene(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.pixMap) # return pixmapitem

    def addSceneToPlayer(self):
        self.player.setScene(self.scene)

    def loadImage(self):
        self.statusBar().showMessage("load image ...")
        self.statusBar().repaint()
        self.setPlayerHeightWidth()
        self.qimage = self.reader.getQImage()
        self.autoscroll()
        self.qimageToPixmap()
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        self.lock = False
        self.statusBar().clearMessage()

    def loadVideo(self):
        self.statusBar().showMessage("play video ...")
        videoScene = self.reader.getVideo()
        self.statusBar().clearMessage()

    def autoscroll(self):
        print("mainWindow.autoscroll()")
        print("mainWindow...maximum(): ", self.scrollArea.verticalScrollBar().maximum())
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        #self.scrollArea.verticalScrollBar().setSliderDown(True)
        #self.scrollArea.repaint()
        #self.repaint()

    def resizeEvent(self, event):
        if self.lock == False:
            print("Event")           
            self.setPlayerHeightWidth()
            self.qimageToPixmap()
            self.resizePixmap()
            self.pixmapSetScene()
            self.addSceneToPlayer()
