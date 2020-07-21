import numpy as np
import cv2
import time
from PyQt5 import QtCore
from PyQt5.QtGui import QImage
from signals import WorkerSignals

class Yolo(QtCore.QRunnable):

    def __init__(self, net, layerNames, mutexNet, tile):
        QtCore.QRunnable.__init__(self)
        print("Yolo.__init__()")
        self.net = net
        self.layerNames = layerNames
        self.mutexNet = mutexNet
        self.frame = tile
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
        run_end = time.time()
        self.mutexNet.unlock()
        print("Yolo.run()_after_detectImage(): " + str(run_end - run_start))
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        qimage = QImage(frame, 512, 512, QImage.Format_BGR888)
        self.signals.output_signal.emit(qimage)


    def detectImage(self): 
        #print("Yolo.detectImage()")
        
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        #self.printBoxes()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        

    def createBlob(self):
        #print("Yolo.createBlob()")        
        start = time.time()
        self.blob = cv2.dnn.blobFromImage(self.frame, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        end = time.time()
        #print("createBlob(): " + str(end - start))       

    def setNetInput(self):
        #print("Yolo.setNetInput()")       
        start = time.time()
        self.net.setInput(self.blob)        
        end = time.time()
        #print("setNetInput(): " + str(end - start))      

    def getOutput(self):
        #print("Yolo.getOutput()")       
        start = time.time()
        self.outs = self.net.forward(self.layerNames)
        end = time.time()
        #print("getOutput(): " + str(end - start))

    def generateBoxes_confidences_classids(self):
        #print("Yolo.generateBoxes_confidence_classids()")       
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

                    string = ("{:3.2f}, {:5d}, {:4d}, {:4d}, {:4d}".format(confidence, x, y, int(bwidth), int(bheight)))

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
        start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                #x_ = x / self.imageHeight
                #y_ = y / self.imageHeight
                #w_ = w / self.imageHeight
                #h_ = h / self.imageHeight
                #x = int(x_ * self.orgSize)
                #y = int(y_ * self.orgSize)
                #w = int(w_ * self.orgSize)
                #h = int(h_ * self.orgSize)
                #print(x, y)
                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes
                cv2.rectangle(self.frame, (x,y), (x + w, y + h), (255,0,0), 2)
        end = time.time()
        #print("drawLabels...() " + str(end - start))
