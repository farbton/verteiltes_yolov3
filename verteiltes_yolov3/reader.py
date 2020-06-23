#import numpy
import os
import cv2
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5 import QtCore 

class Reader(object):
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        #pass

    def load_image(self):
        print("load image ...")
        self.mainWindow.statusBar().showMessage("load image")
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        pixMap = QPixmap(image_name)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.mainWindow.player.setScene(scene)
        self.mainWindow.statusBar().clearMessage()
        

    def load_video(self):
        print("load video ...")
        self.mainWindow.statusBar().showMessage("load video")

        #QtWidgets.QApplication.event()