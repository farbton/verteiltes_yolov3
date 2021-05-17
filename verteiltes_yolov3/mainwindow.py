import sys
import cv2
import os
import platform
import time
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QMouseEvent


#from video_reader_parallel import ReaderParallel
from video_reader_serial import VideoReaderSerial
from image_reader_serial import ImageReaderSerial
from video_reader_live import VideoReaderLive

#Klasse die in das MainWindow schreiben darf
class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("guiNew.ui", self)
        self.console.setFont(QFont('Times', 11))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(True)
        self.player.setSizePolicy(sizePolicy)
        print(self.player.sizePolicy().hasHeightForWidth())
        print(self.player.geometry())

        self.labelWeights.setFont(QFont('Times', 11))
        self.labelCfg.setFont(QFont('Times', 11))
        self.labelData.setFont(QFont('Times', 11))
        self.labelComport.setFont(QFont('Times', 11))
        self.labelWeightsName.setFont(QFont('Times', 11))
        self.labelCfgName.setFont(QFont('Times', 11))
        self.labelDataName.setFont(QFont('Times', 11))
        self.labelComportName.setFont(QFont('Times', 11))
        self.setWindowTitle("YOLO-Viewer")
        self.closeVariable = 0
        self.showDetect = 0
        self.pixMap= None

        icon = QIcon()
        icon.addFile("icons/favicon-16x16.png", QtCore.QSize(16,16))
        icon.addFile("icons/favicon-32x32.png", QtCore.QSize(32,32))
        icon.addFile("icons/favicon-48x48.png", QtCore.QSize(48,48))
        icon.addFile("icons/favicon-192x192.png", QtCore.QSize(192,192))
        icon.addFile("icons/favicon-512x512.png", QtCore.QSize(512,512))
        icon.addFile("icons/icon.png", QtCore.QSize(512,512))
        self.setWindowIcon(icon)
        
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

        #logoPicName = "C:\Insektenlaser\GIT\verteiltes_yolov3\verteiltes_yolov3\icons\favicon-32x32.png"
        #logoPic = QPixmap(logoPicName)
        #scaledlogoPic = logoPic.scaled(QtCore.QSize(50, 50), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        #itemLogo = QtWidgets.QGraphicsPixmapItem(scaledlogoPic)
        #sceneLogo = QtWidgets.QGraphicsScene(self)
        #sceneLogo.addItem(itemLogo)
        #self.graphicsViewLogo.setScene(sceneLogo)
        self.player.setMouseTracking(True)

        self.labelWeights.setText(str(self.weightsFileName.rpartition("/")[2]))
        self.labelCfg.setText(str(self.cfgFileName.rpartition("/")[2]))
        self.labelData.setText(str(self.classesFileName.rpartition("/")[2]))
        self.labelComport.setText("no COM-Port connected")

        self.lock = True
        self.mutexDislpay = QtCore.QMutex()
        self.mutexList = QtCore.QMutex()
        #self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #time.sleep(5)
        #self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # TODO alle wichtigen versionen ausgeben
        # TODO detectierte Käfer ausschneiden zum Monitoring
        # TODO confidence variable über gui änderbar machen
        # SubframeGrid über Bild legen ein- und ausschlatbar über chackbox

        #self.signals = WorkerSignals()
        #self.signals.output_signal.connect(self.display)
        #self.signals.signal_detectionList.connect(self.writeList)
        
    def closeEvent(self, event):
        self.closeVariable=1
        #print(str(self.closeVariable))

    def start(self):        
        self.pushButton_clear.clicked.connect(self.refreshConsoleAndList)
        self.pushButton_detectVideo.clicked.connect(self.loadVideoSerial)
        self.pushButton_detectImage.clicked.connect(self.startDetection)
        self.pushButton_detectLive.clicked.connect(self.detectVideoLive)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_saveImage.clicked.connect(self.saveImage)
        self.actionload_image.triggered.connect(self.loadImageName2048)
        self.actionload_image_512_pix.triggered.connect(self.loadImageName512)
        self.actionload_video_parallel.triggered.connect(self.loadVideoParallel)
        self.actionload_video_serial.triggered.connect(self.loadVideoFile)
        self.actionload_HXC40.triggered.connect(self.showHXC40Live)
        self.actionload_cfg.triggered.connect(self.loadCfgFile)
        self.actionload_weights.triggered.connect(self.loadWeightsFile)
        self.actionload_data.triggered.connect(self.loadDataFile)
        self.actionload_video_info.triggered.connect(self.getVideoInfo)
        self.actionload_detectionLog.triggered.connect(self.getDetectionLog)
        self.actionload_monitorDir.triggered.connect(self.getMonitorDir)

    def saveImage(self):
        #print("save")
        pass

    def getDetectionLog(self):
        os.startfile("detectionLog.txt")

    def getMonitorDir(self):
        os.startfile("C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/monitorImages/")

    def stop(self):
        self.enableButtons()

    def loadWeightsFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .weights:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.weights")
        self.weightsFileName = filename
        string = "weightsFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.labelWeights.setText(str(filename.rpartition("/")[2]))
        self.autoscroll()

    def loadCfgFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .cfg:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.cfg")
        self.cfgFileName = filename
        string = "cfgFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.labelCfg.setText(str(self.cfgFileName.rpartition("/")[2]))
        self.autoscroll()

    def loadDataFile(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a .names:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/yolo', "*.names")
        self.classesFileName = filename
        string = "dataFile: " + str(filename.rpartition("/")[2]) + "\n"
        self.console.setText(self.console.text() + string)
        self.labelData.setText(str(self.classesFileName.rpartition("/")[2]))
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
            self.loadImage()
            self.autoscroll()
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
       # geo = self.player.geometry()
        #print(geo)
        self.playerWidth = self.player.geometry().width()
        self.playerHeight = self.player.geometry().height()

    def convertCv2ToQImage(self, aufloesung):       
        self.qimage = QImage(self.detectedImage, aufloesung[0], aufloesung[1], QImage.Format_RGB888)

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
        if filename:
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
            string = "solution: " + str(aufloesung) + "\n"
            self.console.setText(self.console.text() + string)
            self.autoscroll()

    def loadImageName2048(self):
        (filename, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a image:', 'C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/images')
        if filename:
            self.imageName = filename
            self.detectedImage = cv2.imread(self.imageName)
            self.detectedImage = cv2.cvtColor(self.detectedImage, cv2.COLOR_BGR2RGB)
            aufloesung = self.detectedImage.shape
            self.convertCv2ToQImage(aufloesung)
            self.qimageToPixmap()
            self.resizePixmap()
            self.pixmapSetScene()
            self.addSceneToPlayer()
            string = ".jpg: " + str(self.imageName.rpartition("/")[2] + "\n")
            self.console.setText(self.console.text() + string)
            string = "solution: " + str(aufloesung) + "\n"
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
        string = "detections: " + str(detections) + "\n" + "\n"
        self.console.setText(self.console.text() + string)

        if(self.detectedImage.shape[0] == 512):
            self.convertCv2ToQImage512()
        else:
            
            self.convertCv2ToQImage(self.detectedImage.shape)

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
        self.disableButtons()
        videoReaderSerial = VideoReaderSerial(self, self.weightsFileName, self.cfgFileName, self.classesFileName)
        self.statusBar().showMessage("play video ...")
        videoReaderSerial.getVideo(self.videoFileName)
        self.statusBar().clearMessage()

    def detectVideoLive(self):
        self.disableButtons()
        self.pushButton_stop.setChecked(False)
        self.showDetect = 1
        videoReaderLive = VideoReaderLive(self, self.weightsFileName, self.cfgFileName, self.classesFileName)

    def showHXC40Live(self):
        self.disableButtons()
        self.pushButton_stop.setChecked(False)
        self.showDetect = 0
        videoReaderLive = VideoReaderLive(self, self.weightsFileName, self.cfgFileName, self.classesFileName)
     
    def disableButtons(self):
        self.pushButton_detectVideo.setEnabled(False)
        self.pushButton_detectLive.setEnabled(False)
        self.pushButton_detectImage.setEnabled(False)
        self.lineEditConfidenceThreshold.setEnabled(False)
        QtWidgets.QApplication.processEvents()

    def enableButtons(self):
        self.pushButton_detectVideo.setEnabled(True)
        self.pushButton_detectLive.setEnabled(True)
        self.pushButton_detectImage.setEnabled(True)
        self.lineEditConfidenceThreshold.setEnabled(True)
        QtWidgets.QApplication.processEvents()

    def autoscroll(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()
        
    def resizeEvent(self, event):
        #if self.lock == False:
        if self.pixMap is not None:
            #print("resizeEvent")
            self.setPlayerHeightWidth()
            self.resizePixmap()
            self.pixmapSetScene()
            self.addSceneToPlayer()

    def mousePressEvent(self, event):
        height = self.player.geometry().height()
        width = self.player.geometry().width()
        #diff = (height-width)/2
        #print(str(diff))
        #print(height, width, self.player.frameSize())
        pos = event.pos()
        #print("MainWindowCoordinateMausKlick: " + str(event.pos()))
        #print("GlobalCoordinateWidget: " + str(self.player.pos()))
        #print("mapFromGlobal: " + str(self.player.mapFromGlobal(QtCore.QPoint(event.pos()))))
        globalCoordinate = self.player.mapToGlobal(QtCore.QPoint(event.pos()))
        localCoordinate = self.player.mapFromGlobal(globalCoordinate)
        mapPoints = self.player.mapTo(self.player,QtCore.QPoint(event.pos()))
        #print("mapToGlobal: " + str(globalCoordinate))
        #print("mapFromGlobal: " + str(localCoordinate))
        #print("mapPoints: " + str(mapPoints))
        #print("y: " + str(event.pos().y()))
        #print(self.player.frameGeometry())
        #print(str(event.type()))
        #if event.type() == QMouseEvent:
       # print(str(pos))
        #sp = self.player.mapToScene(pos)
        #lp = self.scaledPixMap.mapFromScene(sp).toPoint()
       # print(str(sp))
        tempX = round((round(2048 / width,2)) * (pos.x()-5),0)
        tempY =round(round(2048/height,2) * (pos.y()-230),0)
        self.labelKoordinaten.setText("x: %d, y: %d" % (tempY, tempX))
        #print(tempX)

    def getVideoInfo(self):
        cap = cv2.VideoCapture(self.videoFileName)
        nString = " \n" + "VideoCaptureBackendName: " + cap.getBackendName() + "\n"
        self.console.setText(self.console.text() + nString)

        fpsString = "fps: " + str(cap.get(cv2.CAP_PROP_FPS)) + "\n"
        self.console.setText(self.console.text() + fpsString)

        cString = "Codec: " + str(cap.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT)) + "\n"
        self.console.setText(self.console.text() + cString)

        whString = "width x height: " + str(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))) + " x " + str(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) + "\n"
        self.console.setText(self.console.text() + whString)

        cap.release()
        self.autoscroll()