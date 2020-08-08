import sys
import cv2
import os, platform
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
from signals import WorkerSignals

from reader_parallel import ReaderParallel
from reader_seriell import ReaderSeriell
#from yolo import Yolo

#Klasse die in das MainWindow schreiben darf
class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Viewer for Yolov3")
        self.imageName = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        self.imageName512 = "images_512/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros840_rot90sub3.jpg"
        self.readerSeriell = ReaderSeriell(self)
        self.readerParallel = ReaderParallel(self)
        self.lock = True
        self.mutexDislpay = QtCore.QMutex()
        self.mutexList = QtCore.QMutex()
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        #QtWidgets.QApplication.processEvents()
        print("Python-Version: " + str(platform.python_version()))
        print("OpenCV-Version: " + str(cv2.__version__))
        #self.signals = WorkerSignals()
        #self.signals.output_signal.connect(self.display)
        #self.signals.signal_detectionList.connect(self.writeList)

    def start(self):        
        #self.refresh_button.clicked.connect(self.label_write)
        #self.actionload_image.triggered.connect(self.loadImage)
        self.actionload_video_parallel.triggered.connect(self.loadVideoParallel)
        self.actionload_video_seriell.triggered.connect(self.loadVideoSeriell)
        #self.pushButtonStartDetection.clicked.connect(self.startDetection)

    #def startDetection(self):
    #    self.console.clear()
    #    print("startDetection")
    #    self.statusBar().showMessage("detection ... ")
    #    self.console.setText(self.console.text() + "start detection ... \n")
    #    self.console.repaint()
    #    self.image = self.reader.getFrame(self.imageName512)
    #    self.detectImage()

    #def detectImage(self):
    #    self.detectedImage = self.yolo.detectImage(self.image)
    #    self.convertCv2ToQImage()
    #    #cv2.imshow("test", self.detectedImage)
    #    self.setPlayerHeightWidth()
    #    self.qimageToPixmap()
    #    self.resizePixmap()
    #    self.pixmapSetScene()
    #    self.addSceneToPlayer()
    #    self.statusBar().clearMessage()
    #    self.console.setText(self.console.text() + "ready ... \n")
    #    self.console.repaint()
    #    self.autoscroll()
    #    self.lock = False

    #def label_write(self):
    #    self.label.setText("hallo")

    def writeList(self, list):
        #self.mutexList.lock()
        print("Mainwindow.writeList()")
        self.listWidget.clear()
        self.listWidget.addItems(list)
        #self.mutexList.unlock()
    
    #def setPlayerHeightWidth(self):
    #    self.playerHeight = self.player.geometry().height()
    #    self.playerWidth = self.player.geometry().width()

    #def convertCv2ToQImage(self):
    #    self.qimage = QImage(self.detectedImage, 512, 512, QImage.Format_BGR888)

    #def qimageToPixmap(self):
    #    self.pixMap = QPixmap(self.qimage)

    #def resizePixmap(self):
    #    self.pixMap = self.pixMap.scaled(QtCore.QSize(self.playerHeight, self.playerWidth), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
    
    #def pixmapSetScene(self):
    #    self.scene = QtWidgets.QGraphicsScene()
    #    self.scene.addPixmap(self.pixMap) # return pixmapitem

    #def addSceneToPlayer(self):
    #    self.player.setScene(self.scene)

    #def loadImage(self):
    #    self.statusBar().showMessage("load image ...")
    #    self.statusBar().repaint()
    #    self.setPlayerHeightWidth()
    #    self.qimage = self.reader.getImage(self.imageName512)
    #    self.autoscroll()
    #   # self.qimageToPixmap()
    #    #self.resizePixmap()
    #    #self.pixmapSetScene()
    #    #self.addSceneToPlayer()
    #    self.lock = False
    #    self.statusBar().clearMessage()

    def loadVideoParallel(self):
        self.statusBar().showMessage("play video ...")
        self.readerParallel.getVideo()
        self.statusBar().clearMessage()


    def loadVideoSeriell(self):
        self.statusBar().showMessage("play video ...")
        self.readerSeriell.getVideo()
        self.statusBar().clearMessage()

    #def autoscroll(self):
    #    print("mainWindow.autoscroll()")
    #    print("mainWindow...maximum(): ", self.scrollArea.verticalScrollBar().maximum())
    #    self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
    #    #self.scrollArea.verticalScrollBar().setSliderDown(True)
    #    #self.scrollArea.repaint()
    #    #self.repaint()

    #def resizeEvent(self, event):
    #    if self.lock == False:
    #        print("Event")           
    #        self.setPlayerHeightWidth()
    #        self.qimageToPixmap()
    #        self.resizePixmap()
    #        self.pixmapSetScene()
    #        self.addSceneToPlayer()

    @QtCore.pyqtSlot(QImage)
    def display(self, frame):
        #self.mutexDislpay.lock()
        print("Mainwindow.display(): ")
        height = self.player.geometry().height()
        width = self.player.geometry().width()
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frameImage = QImage(frame.data, frame.shape[1], frame.shape[0],
        #QImage.Format_RGB888)
        pixMap = QPixmap.fromImage(frame)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.player.setScene(scene)
        #end = time.time()
        #print(end-start)
        #self.mainWindow.console.clear()
        QtWidgets.QApplication.processEvents()
        #self.mutexDislpay.unlock()