import sys
import cv2
import os
import platform
import time
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon


from video_reader_parallel import ReaderParallel
from video_reader_serial import VideoReaderSerial
from image_reader_serial import ImageReaderSerial
from video_reader_live import ReaderLive

#Klasse die in das MainWindow schreiben darf
class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)
        self.console.setFont(QFont('Times', 9))
        self.setWindowTitle("Viewer for Yolov")
        self.setWindowIcon(QIcon("icon.png"))
        
        pString = "Python-Version: " + str(platform.python_version() + "\n")
        self.console.setText(self.console.text() + pString)
        
        cvString = "OpenCV-Version: " + str(cv2.__version__ + "\n" + "\n")
        self.console.setText(self.console.text() + cvString)

        self.imageName = "images_512/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros840_-50_rot270sub3.jpg"
        iString = ".jpg: " + str(self.imageName.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + iString)
                        
        self.weightsFileName = "yolo/yolov4-tiny-kirko_best.weights"
        wfString = ".weights: " + str(self.weightsFileName.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + wfString)

        self.cfgFileName = "yolo/yolov4-tiny-kirko.cfg"
        cfgString = ".cfg: " + str(self.cfgFileName.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + cfgString)

        self.classesFileName = "yolo/weevil.names"
        dataString = ".names: " + str(self.classesFileName.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + dataString)

        self.videoFileName = "videos/12-12-2019 MONO 30fps 11_51_25_Testvideo_10s.avi" 
        vnString = ".avi: " + str(self.videoFileName.rpartition("/")[2]) + "\n" + "\n"
        self.console.setText(self.console.text() + vnString)

        #self.readerSeriell = ReaderSeriell(self)
        #self.readerParallel = ReaderParallel(self)
        
        #self.readerLive = ReaderLive(self)
        self.lock = True
        self.mutexDislpay = QtCore.QMutex()
        self.mutexList = QtCore.QMutex()
        #self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #time.sleep(5)
        #self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # TODO alle wichtigen versionen ausgeben
        #self.signals = WorkerSignals()
        #self.signals.output_signal.connect(self.display)
        #self.signals.signal_detectionList.connect(self.writeList)

    def start(self):        
        self.refresh_button.clicked.connect(self.refreshConsoleAndList)
        self.pushButton_detectVideo.clicked.connect(self.loadVideoSerial)
        self.actionload_image.triggered.connect(self.loadImageName2048)
        self.actionload_image_512_pix.triggered.connect(self.loadImageName512)
        self.actionload_video_parallel.triggered.connect(self.loadVideoParallel)
        self.actionload_video_serial.triggered.connect(self.loadVideoFile)
        self.actionload_HXC40.triggered.connect(self.loadLiveVideo)
        self.actionload_cfg.triggered.connect(self.loadCfgFile)
        self.actionload_weights.triggered.connect(self.loadWeightsFile)
        self.actionload_data.triggered.connect(self.loadDataFile)
        self.pushButtonStartDetection.clicked.connect(self.startDetection)

    def loadWeightsFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .weights:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.weights")
        self.weightsFileName = filename
        string = "weightsFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def loadCfgFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .cfg:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.cfg")
        self.cfgFileName = filename
        string = "cfgFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def loadDataFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .names:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.names")
        self.classesFileName = filename
        string = "dataFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def loadVideoFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .avi:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/videos', "*.avi")
        self.videoFileName = filename
        string = "videoFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def startDetection(self):
        if(self.imageName != ""):
            self.statusBar().showMessage("detection ...  ")
            self.console.setText(self.console.text() + "\nstart detection ...  \n")
            self.autoscroll()
            self.loadImage()
        else:
            self.console.setText(self.console.text() + "Bitte Image auswählen ...  \n")
            self.autoscroll()  

    def refreshConsoleAndList(self):
        self.console.clear()
        self.listWidget.clear()

    def writeList(self, list):
        #self.mutexList.lock()
        print("Mainwindow.writeList()")
        self.listWidget.clear()
        self.listWidget.addItems(list)
        #self.mutexList.unlock()
    
    def setPlayerHeightWidth(self):
        self.playerHeight = self.player.geometry().height()
        self.playerWidth = self.player.geometry().width()

    def convertCv2ToQImage2048(self):
        self.qimage = QImage(self.detectedImage, 2048, 2048, QImage.Format_RGB888)

    def convertCv2ToQImage512(self):
        self.qimage = QImage(self.detectedImage, 512, 512, QImage.Format_RGB888)

    def qimageToPixmap(self):
        self.pixMap = QPixmap(self.qimage)

    def resizePixmap(self):
        height = self.player.geometry().height()
        width = self.player.geometry().width()
        self.scaledPixMap = self.pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        
    def pixmapSetScene(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.scaledPixMap) # return pixmapitem

    def addSceneToPlayer(self):
        self.player.setScene(self.scene)

    def loadImageName512(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a image:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/images_512')
        self.imageName = filename
        self.detectedImage = cv2.imread(self.imageName)
        aufloesung = self.detectedImage.shape
        self.convertCv2ToQImage512()
        self.qimageToPixmap()
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        string = "loaded file: " + str(filename.rpartition("/")[2] + "\n")
        self.console.setText(self.console.text() + string)
        string = "Auflösung: " + str(aufloesung) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def loadImageName2048(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a image:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/images')
        self.imageName = filename
        self.detectedImage = cv2.imread(self.imageName)
        aufloesung = self.detectedImage.shape
        self.convertCv2ToQImage2048()
        self.qimageToPixmap()
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        string = "loaded file: " + str(filename + "\n")
        self.console.setText(self.console.text() + string)
        string = "Auflösung: " + str(aufloesung) + "\n"
        self.console.setText(self.console.text() + string)
        self.autoscroll()

    def loadImage(self):       
        imageReaderSerial = ImageReaderSerial(self, self.cfgFileName, self.weightsFileName, self.classesFileName)
        self.statusBar().showMessage("load image ...")
        self.statusBar().repaint()
        self.setPlayerHeightWidth()
        self.setPlayerHeightWidth()
        string = self.console.text() + "detectImage ...  "
        self.console.setText(string)
        start = time.time()
        self.detectedImage, detections = imageReaderSerial.getImage(self.imageName)
        end = time.time()
        #cv2.imshow(" k " , self.detectedImage512)
        string = self.console.text() + "{:2f} s \n".format(end - start)
        self.console.setText(string)
        string = "Detektionen: " + str(detections) + "\n"
        self.console.setText(self.console.text() + string)
        if(self.detectedImage.shape[0] == 512):
            self.convertCv2ToQImage512()
        else:
            self.convertCv2ToQImage2048()
        self.qimageToPixmap()
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        self.lock = False
        self.statusBar().clearMessage()
        self.autoscroll()

    def loadVideoParallel(self):
        self.statusBar().showMessage("play video ...")
        self.readerParallel.getVideo()
        self.statusBar().clearMessage()    

    def loadVideoSerial(self):
        readerSerial = VideoReaderSerial(self, self.weightsFileName, self.cfgFileName, self.classesFileName)
        self.statusBar().showMessage("play video ...")
        readerSerial.getVideo(self.videoFileName)
        self.statusBar().clearMessage()

    def loadLiveVideo(self):
        
        self.statusBar().showMessage("play video ...")
        self.readerLive.getVideo()
        self.statusBar().clearMessage()

    def autoscroll(self):
        QtWidgets.QApplication.processEvents()
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        
    def resizeEvent(self, event):
        if self.lock == False:
            #print("Event")
            self.setPlayerHeightWidth()
            #self.qimageToPixmap()
            #pixmap = self.player.items()
            #pixmap = pixmap[0].pixmap()
            #print(pixmap)
            self.resizePixmap()
            self.pixmapSetScene()
            self.addSceneToPlayer()

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