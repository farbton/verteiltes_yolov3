from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import numpy as np
import serial
import functions

class ImageReaderSerial(QtCore.QObject):
    def __init__(self, mainWindow, cfgFileName, weightsFileName, classesFileName):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        self.cfgFileName = cfgFileName 
        self.weightsFileName = weightsFileName
        self.classesFileName = classesFileName
        
        try:
            self.ser = serial.Serial('COM4', 115200)
            print("self.ser: " , self.ser)
            print("Serialname: " , self.ser.name)
            time.sleep(2)
            self.ser.write(b'cls quad conf x y \n')
            self.ser.flush()
            sString = "COM-Port: " + self.ser.name + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
        except:
            sString = "Kein COM-Port verfügbar \n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)

        strich = "========================================================\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + strich)

        self.conf_threshhold = 0.9 
        self.nms_treshold = 0.5
        self.counter = 1
        self.netTime = 0
        self.netTimeList = []
        self.oneCycleList = []
        self.getClassesNames()
        self.readNet()
        self.setLayerNames()

    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFileName, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def readNet(self):
        string = self.mainWindow.console.text() + "reader_seriell readNet() ...  "
        self.mainWindow.console.setText(string)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFileName)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)

    def setLayerNames(self):
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def getImage(self, filename):
        self.tile = cv2.imread(filename)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxesImage()
        self.writeList()
        return self.tile, len(self.idxs)

    def modCount(self):
        self.modCounter = self.counter % 16
   
    def createBlob(self):
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.tile.shape[0], self.tile.shape[1]), [0,0,0], 1, crop=False)

    def setNetInput(self):
        self.net.setInput(self.blob)        

    def getOutput(self):
        self.outs = self.net.forward(self.layerNames)

    def generateBoxes_confidences_classids(self):
        self.boxes = []
        self.confidences = []
        self.classids = []

        for out in self.outs:
            for detection in out:

                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]

                if confidence > 0.8:
                    box = detection[0:4] * np.array([self.tile.shape[0], self.tile.shape[1], self.tile.shape[0], self.tile.shape[1]])
                    centerX, centerY, bwidth, bheight = box.astype('int')
                
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    self.boxes.append([x,y, int(bwidth), int(bheight)])                   
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)

    def nonMaximaSupress(self):
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)

    def drawLabelsAndBoxesImage(self):
        self.boxesString = []
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], x, y))
                self.boxesString.append(string)
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)               
       
    def writeList(self):
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(self.boxesString)
        

    

    
