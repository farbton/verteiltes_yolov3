import numpy as np
import os
import cv2
import time
#import _thread
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from signals import WorkerSignals

from PyQt5.QtGui import QImage, QPixmap
import yoloQRunnable 

class ReaderParallel(QtCore.QObject):
    def __init__(self, mainWindow):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        self.signals = WorkerSignals()
        self.threadPool = QtCore.QThreadPool()
        #self.threadPool.setMaxThreadCount(1)
        self.mutexNet = QtCore.QMutex()
        self.mutexDislpay = QtCore.QMutex()
        self.mutexList = QtCore.QMutex()
        self.cfgFileName = "yolo/yolov3.cfg" 
        self.weightsFile = "yolo/yolov3_512.weights" 
        self.classesFile = "yolo/weevil.names"
        self.prepareNet()
    
    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def printClassesNames(self):
        #self.mainWindow.listWidget.addItems(self.classes)
        pass

    #def setColors(self):
    #    self.colors = np.random.randint(0, 255, size=(len(self.classes), 3),
    #    dtype='uint8')

    def readNet(self):
        #print("Reader.readNet()")
        string = self.mainWindow.console.text() + "reader_parallel read net ...  "
        self.mainWindow.console.setText(string)
        #self.mainWindow.console.repaint()
        #self.autoscroll()
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFile)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        #self.mainWindow.console.repaint()
        #self.autoscroll()

    def setLayerNames(self):
        #print("Reader.setLayerNames()")
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        #print(self.layerNames)

    def prepareNet(self):
        #print("Reader.prepareNet()")
        self.getClassesNames()
        self.printClassesNames()
        #self.setColors()
        self.readNet()
        self.setLayerNames()

    def getImage(self, imageName):
        print("reader.getImage()")
        frame = cv2.imread(imageName)
        yolo_ = yolo.Yolo(frame)
        detectedFrame = yolo_.detectImage(frame)
        self.display(detectedFrame)
        #return detectedFrame


    def getQImage(self, imageName):
        string = self.mainWindow.console.text() + "load image file ..." + imageName + "\n"
        self.mainWindow.console.setText(string)
        return QImage(imageName)
   
    def getFrame(self, name):
        frame = cv2.imread(name)
        return frame

    def getVideo(self):
        #print("load video ...")
        videoName = "videos/12-12-2019 MONO 30fps 11_51_25_Testvideo_10s.avi"
        string = self.mainWindow.console.text() + "load video file ..." + videoName + "\n"
        self.mainWindow.console.setText(string)
        
        cap = cv2.VideoCapture(videoName)
        print("fps: " + str(cap.get(cv2.CAP_PROP_FPS)))
        print("codec: " + str(cap.get(cv2.CAP_PROP_FOURCC)))
        counter = 1
        while(cap.isOpened() and counter <= 6):
            #start = time.time()
            ret,frame = cap.read()
            if ret == False:
                break
            yoloThread = yoloQRunnable.Yolo(self.mainWindow, self.net, self.layerNames, self.mutexNet, frame, counter)
            #print("vor start: " + str(self.yoloThread.thread()))
            yoloThread.signals.output_signal.connect(self.display)
            yoloThread.signals.signal_detectionList.connect(self.writeList)
            self.threadPool.start(yoloThread)
            #yoloThread.start()
            #print("ThreadPool: " + str(self.threadPool.activeThreadCount()) + " counter: " + str(counter) )
            counter += 1
            QtWidgets.QApplication.processEvents()
            #time.sleep(0.4)
            
        #cap.release()
    
    def writeList(self, list):
        self.mutexList.lock()
        print("Mainwindow.writeList()")
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(list)
        self.mutexList.unlock()

    #@QtCore.pyqtSlot(QImage)
    def display(self, frame):
        self.mutexDislpay.lock()
        print("Reader.display(): ")
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frameImage = QImage(frame.data, frame.shape[1], frame.shape[0],
        #QImage.Format_RGB888)
        pixMap = QPixmap.fromImage(frame)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.mainWindow.player.setScene(scene)
        self.mutexDislpay.unlock()
        #end = time.time()
        #print(end-start)
        #self.mainWindow.console.clear()
        QtWidgets.QApplication.processEvents()

    