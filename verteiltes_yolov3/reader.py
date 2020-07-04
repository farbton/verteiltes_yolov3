#import numpy as np
import os
import cv2
#import time
from PyQt5 import QtWidgets

from PyQt5.QtGui import QImage

class Reader(object):
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
          
    def getQImage(self):
        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        string = self.mainWindow.console.text() + "load image file ..." + image_name + "\n"
        self.mainWindow.console.setText(string)
        #self.image = cv2.imread(image_name)
        #QImage(self.image, 512, 512, QImage.Format_RGB888)
        return QImage(image_name)
   
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
        