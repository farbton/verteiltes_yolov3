#import numpy
import os
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtWidgets
from PyQt5 import QtCore 

class Reader(object):
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.cfgFileName = "yolo/yolov3.cfg" 
        self.weightsFile = "yolo/yolov3.weights"
        #pass

    def getImage(self):
        print("getImage(self, height, width)")
        self.setHeightWidth()
        self.loadPixmap()
        # Abgriff der pixmap zur Verarbeitung im CNN
        self.resizePixmap()
        self.pixmapSetScene()
        return self.scene
    
    def loadYolofromDarknet(self):
        self.getClassesNames()
        self.printClassesNames()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFile)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def printClassesNames(self):
        self.mainWindow.listWidget.addItems(self.classes)

    def getClassesNames(self):
        classesFile = "yolo/weevil.names";
        self.classes = None
        with open(classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def setHeightWidth(self):
        self.height = self.mainWindow.player.geometry().height()
        self.width = self.mainWindow.player.geometry().width()
        
    def loadPixmap(self):
        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        self.pixMap = QPixmap(image_name)

    def resizePixmap(self):
        self.pixMap = self.pixMap.scaled(QtCore.QSize(self.height, self.width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
    
    def pixmapSetScene(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.pixMap) # return pixmapitem

    def getVideo(self):
        print("load video ...")       
        videoName = "videos/YOLOv3_output_29.05.2020_10s.avi"
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        cap = cv2.VideoCapture(videoName)
        #timer = QtCore.QTimer()
        while(cap.isOpened()):
            ret,frame = cap.read()
            #self.mainWindow.statusBar().showMessage(timer.remainingTime())
            #print(timer.remainingTime())
            if ret == False:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frameImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixMap = QPixmap.fromImage(frameImage)
            pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            scene = QtWidgets.QGraphicsScene()
            scene.addPixmap(pixMap) # return pixmapitem
            self.mainWindow.player.setScene(scene)
            QtWidgets.QApplication.processEvents()
        