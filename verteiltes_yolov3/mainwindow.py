import sys
from PyQt5 import QtWidgets, uic

from reader import Reader
from yolo import Yolo

#Klasse die in das MainWindow schreiben darf
class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Viewer for Yolov3")
        self.reader = Reader(self)
        self.yolo = Yolo()

    def start(self):        
        self.refresh_button.clicked.connect(self.label_write)
        self.actionload_image.triggered.connect(self.loadImage)
        self.actionload_video.triggered.connect(self.loadVideo)
        self.pushButtonStartDetection.clicked.connect(self.startDetection)

    def startDetection(self):
        print("startDetection")
        self.statusBar().showMessage("detection ... ")
        string = self.console.text() + "start detection ... \n"
        self.console.setText(string)
        self.console.repaint()
        self.repaint()
        self.reader.loadYolofromDarknet()
        self.statusBar().clearMessage()
        self.console.setText(self.console.text() + "ready ... \n")

    def label_write(self):
        self.label.setText("hallo")
     
    def loadImage(self):
        self.statusBar().showMessage("load image ...")
        self.statusBar().repaint()
        height = self.player.geometry().height()
        width = self.player.geometry().width()
        #imageScene = self.reader.getImage()
        #self.player.setScene(imageScene)
        #self.statusBar().clearMessage()

    def loadVideo(self):
        self.statusBar().showMessage("play video ...")
        videoScene = self.reader.getVideo()
        self.statusBar().clearMessage()

    def resizeEvent(self, event):
        print("Event")
        #self.loadImage()

    #def refresh_graphicView_image(self, pix_map_item):
    #    scene = QtWidgets.QGraphicsScene()
    #    scene.addItem(pix_map_item)
    #    self.graphicsView.setScene(scene)
    #    return

