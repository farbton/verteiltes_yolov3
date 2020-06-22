#import numpy
import os
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5 import QtCore 

class Reader(object):
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        #pass

    def read_image(self):
        print("read image ...")
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        #print(geo)

        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        pix_map = QPixmap(image_name)
        #pix_map.scaled(geo)
        pix_map = pix_map.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        pix_map_item = QtWidgets.QGraphicsPixmapItem(pix_map)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(pix_map_item)
        self.mainWindow.player.setScene(scene)
