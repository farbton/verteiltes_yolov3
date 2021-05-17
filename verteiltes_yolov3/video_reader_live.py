from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import numpy as np
import serial
import functions
import siso_board 

class VideoReaderLive(QtCore.QObject):
    def __init__(self, mainWindow, weightsFileName, cfgFileName, classesFileName):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        self.weightsFileName = weightsFileName
        self.cfgFileName = cfgFileName
        self.classesFileName = classesFileName        
               
        try:
            self.ser = serial.Serial('COM5', 9600)
            self.ser.write(b'hello here is the weevil hunter\'s eye \n')
            self.ser.write(b'class quadrant confidence x y \n')
            sString = "COM-Port: " + self.ser.name + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
            self.mainWindow.labelComport.setText(str(self.ser.name) + "/" + str(self.ser.baudrate))
        except:
            sString = "no COM-Port avalible \n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)

        time.sleep(2)
        
        self.imageHeight = 512
        self.imageWidth = 512         
        self.nms_treshold = 0.5
        self.counter = 1
        self.monitorImageCounter = 1
        self.netTime = 0
        self.netTimeList = []
        self.oneCycleList = []

        if self.mainWindow.lineEditConfidenceThreshold.text():
            self.confChanged()
        else:
            self.conf_threshhold = 0.8
            self.mainWindow.lineEditConfidenceThreshold.setText(str(self.conf_threshhold))

        self.mainWindow.lineEditConfidenceThreshold.editingFinished.connect(self.confChanged)
        
        self.getClassesNames()
        self.readNet()
        self.setLayerNames()
        
        self.boardThread = siso_board.SisoBoard(self.mainWindow) 
        
        if self.mainWindow.showDetect == 1:
            self.boardThread.signals.live_image.connect(self.detectImage)
        else:
            self.boardThread.signals.live_image.connect(self.showImage)

        self.boardThread.run()
    
    def confChanged(self):
        tempText = self.mainWindow.lineEditConfidenceThreshold.text()
        tempText = tempText.replace(',','.')
        self.conf_threshhold = float(tempText)
    
    def test(self):
        print("fertig")


    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFileName, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def readNet(self):
        string = self.mainWindow.console.text() + "reader_seriell read net ...  "
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

    def modCount(self):
        self.modCounter = self.counter % 16
        self.counter += 1
   
    def createBlob(self):     
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)

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

                if confidence > self.conf_threshhold:
                    box = detection[0:4] * np.array([self.imageWidth, self.imageHeight, self.imageWidth, self.imageHeight])
                    centerX, centerY, bwidth, bheight = box.astype('int')
                
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    self.boxes.append([x,y, int(bwidth), int(bheight)])                   
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)


    def printBoxes(self):
        pass
        #self.mainWindow.listWidget.addItems(self.boxes)

    def nonMaximaSupress(self):
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)

    def writeLog(self, class_, stringLog):
        listValue = str(self.detections) + " " + \
            str(self.classes[class_]) + \
            " detection(s) on | " + \
            str(time.asctime()) + " | " + \
            stringLog + \
            " ImageNr: " + \
            str(self.monitorImageCounter) + \
            " \n"
        self.detectionListFile = open("detectionLog.txt", "a")
        self.detectionListFile.write(listValue)
        self.detectionListFile.close()

    def drawLabelsAndBoxes(self):

        self.boxesString = []
        self.detections = 0
        self.processtime = 0

        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                global_x, global_y = functions.getGlobalCoordinates(self.modCounter, y, x)
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], global_x, global_y))
             
                serString = str(global_x).encode('utf-8') + str(' ').encode('utf-8') + \
                   str(global_y).encode('utf-8') + str(' ').encode('utf-8') + \
                   str('\n').encode('utf-8')
                self.ser.write(serString)

                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes

                self.boxesString.append(string) 
                monitorImage = self.tile[y - 5:y + h,x - 5:x + w]
                miString = "monitorImages\monitorImage_" + str(self.monitorImageCounter) + ".jpg"
                if monitorImage.size != 0:
                    cv2.imwrite(miString,monitorImage)
                    self.monitorImageCounter += 1
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
                self.detections = len(self.idxs)
                if self.detections > 0:
                    class_ = self.classids[i]
                    stringLog = "confidence: {:3.2f} x={:4d} y={:4d}".format(self.confidences[i], global_x, global_y) 
                    self.writeLog(class_, stringLog)
                    
                    
        else:
            #cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
            #cv2.putText(self.tile, "X", (256, 256), cv2.FONT_HERSHEY_SIMPLEX,
            #5, (255,0,0))
            pass
 
    #@QtCore.pyqtSlot(np.ndarray)
    def detectImage(self, ndarray): 
        #print("ndarray.shape: ",ndarray.shape)
        frame3d = np.ndarray((2048, 2048, 3), dtype=np.uint8)      
        frame3d[:,:,0] = ndarray
        frame3d[:,:,1] = ndarray
        frame3d[:,:,2] = ndarray

        self.modCount()
        self.tile = functions.getTile(self.modCounter, frame3d)
        time_start = time.time()
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        time_end = time.time()
        self.frame = functions.concatTileAndFrame(self.modCounter, frame3d, self.tile)
        self.processtime = time_end - time_start
        self.writeList()
        self.display()
        
    def showImage(self, ndarray):
        self.frame = ndarray
        width = self.mainWindow.player.geometry().width()
        #self.mainWindow.player.resize(width, width)
        #self.mainWindow.listWidget.resize(width, width)
        #self.mainWindow.console.resize(width, width)
        height = self.mainWindow.player.geometry().height()
        self.frame = QImage(self.frame, 2048, 2048, QImage.Format_Grayscale8)
        pixMap = QPixmap.fromImage(self.frame)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.mainWindow.player.setScene(scene)  
        if self.mainWindow.pushButton_saveImage.isChecked():
            stringName = "IZMImages/test_" + str(time.time()) + ".jpg"
            cv2.imwrite(stringName, ndarray)
            self.mainWindow.pushButton_saveImage.setChecked(False)
        self.autoscroll()
        QtWidgets.QApplication.processEvents()

    def display(self):
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        self.frame = QImage(self.frame, 2048, 2048, QImage.Format_RGB888)
        pixMap = QPixmap.fromImage(self.frame)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.mainWindow.player.setScene(scene)
        self.mainWindow.player.setMouseTracking(True)
        QtWidgets.QApplication.processEvents()
        self.end_time = time.time()
        dString = "detections: " + str(self.detections) + " time: " + str(round(self.processtime,3)) + " s"
        self.mainWindow.labelTimeOutput.setText(dString)
        self.autoscroll()
        #self.oneCycleList.append(self.end_time - self.begin_time)
        #print("ser_oneCycle: " + str(round(self.end_time - self.begin_time,3))
        #+ " netTime: " + str(round(self.netTime,3)))

    def writeList(self):
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(self.boxesString)

    def autoscroll(self):
        self.mainWindow.scrollArea.verticalScrollBar().setValue(self.mainWindow.scrollArea.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()

    
