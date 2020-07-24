import numpy as np
import cv2
import time
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage
from signals import WorkerSignals

class Yolo(QtCore.QRunnable):

    def __init__(self, net, layerNames, mutexNet, frame, counter):
        QtCore.QRunnable.__init__(self)
        print("Yolo.__init__(), counter: " + str(counter))
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
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        qimage = QImage(frame, 2048, 2048, QImage.Format_RGB888)
        run_end = time.time()
        self.mutexNet.unlock()
        self.signals.output_signal.emit(qimage)
        self.signals.signal_detectionList.emit(self.boxesString)
        QtWidgets.QApplication.processEvents()
        #QtCore.QEventLoop.processEvents(QtCore.QEventLoop.AllEvents)
        print("Yolo.run()_after_detectImage(): " + str(run_end - run_start))
        #self.exec_(QtCore.QEventLoop.AllEvents)

    def detectImage(self): 
        #print("Yolo.detectImage()")
        self.modCounter()
        self.tile = self.getTile()
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        #self.printBoxes()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        self.concatTileAndFrame()
        
    def createBlob(self):
        #print("Yolo.createBlob()")
        start = time.time()
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
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
        self.boxesString = []
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
                    self.boxesString.append(string)
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
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
        end = time.time()
        #print("drawLabels...() " + str(end - start))

    def modCounter(self):
        self.modCounter = self.counter % 16
        print("modCounter: " + str(self.modCounter))

    def getTile(self):
        print("getTile()")
        switch = {
            1: self.frame[0:512, 0:512],
            2: self.frame[0:512, 512:1024], 
            3: self.frame[0:512, 1024:1536],
            4: self.frame[0:512, 1536:2048],
            5: self.frame[512:1024, 0:512],
            6: self.frame[512:1024, 512:1024],
            7: self.frame[512:1024, 1024:1536],
            8: self.frame[512:1024, 1536:2048],
            9: self.frame[1024:1536, 0:512],
            10: self.frame[1024:1536, 512:1024],
            11: self.frame[1024:1536, 1024:1536],
            12: self.frame[1024:1536, 1536:2048],
            13: self.frame[1536:2048, 0:512],
            14: self.frame[1536:2048, 512:1024],
            15: self.frame[1536:2048, 1024:1536],
            0 : self.frame[1536:2048, 1536:2048],
            }
        return switch.get(self.modCounter, "fail")

    def counter1(self):
            print("counter1()")
            self.frame[0:512, 0:512] = self.tile

    def counter2(self):
        print("counter2()")
        self.frame[0:512, 512:1024] = self.tile

    def counter3():
        print("counter3()")
        self.frame[0:512, 1024:1536] = self.tile

    def counter4():
        print("counter4()")
        self.frame[0:512, 1536:2048] = self.tile

    def counter5():
        print("counter5()")
        self.frame[512:1024, 0:512] = self.tile

    def counter6():
        print("counter6()")
        self.frame[512:1024, 512:1024] = self.tile

    def counter7():
        print("counter7()")
        self.frame[512:1024, 1024:1536] = self.tile

    def counter8():
        print("counter8()")
        self.frame[512:1024, 1536:2048] = self.tile

    def concatTileAndFrame(self):
        print("concatTileAndFrame()")

        switch = {
            1: self.counter1,
            2: self.counter2, 
            3: self.counter3,
            4: self.counter4,
            5: self.counter5,
            6: self.counter6,
            7: self.counter7,
            8: self.counter8,
            9: self.frame[1024:1536, 0:512],
            10: self.frame[1024:1536, 512:1024],
            11: self.frame[1024:1536, 1024:1536],
            12: self.frame[1024:1536, 1536:2048],
            13: self.frame[1536:2048, 0:512],
            14: self.frame[1536:2048, 512:1024],
            15: self.frame[1536:2048, 1024:1536],
            0 : self.frame[1536:2048, 1536:2048],
            }
        switch.get(self.modCounter, lambda :  "fail") 