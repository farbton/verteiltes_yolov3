import numpy as np
import cv2
import time
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage
from signals import WorkerSignals
import functions

class Yolo(QtCore.QThread):

    def __init__(self, mainWindow, net, layerNames, mutexNet, frame, counter):
        QtCore.QThread.__init__(self)
        #print("QRunnable.__init__(), counter: " + str(counter))
        self.mainWindow = mainWindow
        self.net = net
        self.layerNames = layerNames
        self.mutexNet = mutexNet
        self.frame = frame
        self.counter = counter
        self.imageHeight = 512
        self.imageWidth = 512
        self.conf_threshhold = 0.9 
        self.nms_treshold = 0.9
        self.signals = WorkerSignals()

        
    def run(self):
        #print("Yolo.run()")
        self.mutexNet.lock()
        run_start = time.time()
        self.detectImage()
        qimage = QImage(self.frame, 2048, 2048, QImage.Format_RGB888)
        run_end = time.time()
        self.signals.output_signal.emit(qimage)
        self.signals.signal_detectionList.emit(self.boxesString)
        self.mutexNet.unlock()
        QtWidgets.QApplication.processEvents()
        #QtCore.QEventLoop.processEvents(QtCore.QEventLoop.AllEvents)
        #print("QRunnable.run()_after_detectImage(): " + str(run_end - run_start))
        #string = "QRunnable.run(): " + str(round(run_end - run_start,4)) + "\n"              
        #self.mainWindow.console.setText(self.mainWindow.console.text() + string)
        #self.mainWindow.scrollArea.verticalScrollBar().setValue(self.mainWindow.scrollArea.verticalScrollBar().maximum())
        #self.mainWindow.scrollArea.verticalScrollBar().setSliderDown(True)
        #self.exec_(QtCore.QEventLoop.AllEvents)

    def detectImage(self): 
        #print("Yolo.detectImage()")
        self.modCount()
        #self.tile = self.getTile()
        self.tile = functions.getTile(self.modCounter,self.frame)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        #self.printBoxes()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        self.frame = functions.concatTileAndFrame(self.modCounter,self.frame,self.tile)
        
    def createBlob(self):
        #print("QRunnable.createBlob()")
        start = time.time()
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        end = time.time()
        #print("createBlob(): " + str(end - start))

    def setNetInput(self):
        #print("QRunnable.setNetInput()")
        start = time.time()
        self.net.setInput(self.blob)        
        end = time.time()
        #print("setNetInput(): " + str(end - start))

    def getOutput(self):
        #print("QRunnable.getOutput()")
        start = time.time()
        self.outs = self.net.forward(self.layerNames)
        end = time.time()
        #print("getOutput(): " + str(end - start))

    def generateBoxes_confidences_classids(self):
        #print("QRunnable.generateBoxes_confidence_classids()")
        start = time.time()
        self.boxes = []       
        self.confidences = []
        self.classids = []

        for out in self.outs:
            for detection in out:

                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]

                if confidence > 0.8:
                    box = detection[0:4] * np.array([self.imageWidth, self.imageHeight, self.imageWidth, self.imageHeight])
                    centerX, centerY, bwidth, bheight = box.astype('int')
                
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))
                   
                    #self.mainWindow.listWidget.addItem(string)
                    #self.mainWindow.listWidget.repaint()
                    #self.mainWindow.repaint()
                    self.boxes.append([x,y, int(bwidth), int(bheight)])
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)
                    #print("length: " + str(len(self.confidences)))

        #self.mainWindow.listWidget.addItem(self.boxes)
        end = time.time()
        #print("generate_boxes...() " + str(end - start))

    def printBoxes(self):
        pass
        #self.mainWindow.listWidget.addItems(self.boxes)

    def nonMaximaSupress(self):
        #print("Yolo.nonMaximaSupress()")
        start = time.time()
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)
        end = time.time()
        #print("nonMaximaSupress() " + str(end - start))

    def drawLabelsAndBoxes(self):
        #print("Yolo.drawLabelsAndBoxes()")
        self.boxesString = []
        start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                global_x, global_y = functions.getGlobalCoordinates(self.modCounter, x, y)
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], global_x, global_y))
                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes
                #string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], x, y))
                self.boxesString.append(string)
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
        end = time.time()
        #print("drawLabels...() " + str(end - start))

    def modCount(self):
        self.modCounter = self.counter % 16
        #print("QRunnable.modCount(): modcounter=" + str(self.modCounter))

