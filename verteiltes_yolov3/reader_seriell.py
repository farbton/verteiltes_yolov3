from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import numpy as np
import serial
from functions import FuncSerial


class ReaderSeriell(QtCore.QObject):
    def __init__(self, mainWindow):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        self.cfgFileName = "yolo/yolov3.cfg" 
        self.weightsFile = "yolo/yolov3_512.weights" 
        self.classesFile = "yolo/weevil.names"
        self.ser = serial.Serial('COM10', 9600)
        print("Serialname: " , self.ser.name)
        self.ser.write(b'hello here is the weevil hunter\'s eye \n')
        self.ser.write(b'class quadrant confidence x y \n')
        sString = "COM-Port: " + self.ser.name + "\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
        strich = "========================================================\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + strich)
        self.imageHeight = 512
        self.imageWidth = 512
        self.conf_threshhold = 0.9 
        self.nms_treshold = 0.5
        self.counter = 1
        self.getClassesNames()
        self.readNet()
        self.setLayerNames()

    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def readNet(self):
        #print("Reader.readNet()")
        string = self.mainWindow.console.text() + "reader_seriell read net ...  "
        self.mainWindow.console.setText(string)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFile)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)

    def setLayerNames(self):
        #print("Reader.setLayerNames()")
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        #print(self.layerNames)

    def modCount(self):
        start = time.time()
        self.modCounter = self.counter % 16
        end = time.time()
        print("modCount(): " + str(end - start))
        #print("modCounter: " + str(self.modCounter))    

    def createBlob(self):
        #print("ReaderSeriell.createBlob()")
        start = time.time()
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        end = time.time()
        print("createBlob(): " + str(end - start))

    def setNetInput(self):
        #print("ReaderSeriell.setNetInput()")
        start = time.time()
        self.net.setInput(self.blob)        
        end = time.time()
        print("setNetInput(): " + str(end - start))

    def getOutput(self):
        #print("ReaderSeriell.getOutput()")
        start = time.time()
        self.outs = self.net.forward(self.layerNames)
        end = time.time()
        print("getOutput(): " + str(end - start))

    def generateBoxes_confidences_classids(self):
        #print("ReaderSeriell.generateBoxes_confidence_classids()")
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

                    self.boxes.append([x,y, int(bwidth), int(bheight)])                   
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)

        end = time.time()
        print("generate_boxes...() " + str(end - start))

    def printBoxes(self):
        pass
        #self.mainWindow.listWidget.addItems(self.boxes)

    def nonMaximaSupress(self):
        #print("Yolo.nonMaximaSupress()")
        start = time.time()
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)
        end = time.time()
        print("nonMaximaSupress() " + str(end - start))

    def drawLabelsAndBoxes(self):
        #print("Yolo.drawLabelsAndBoxes()")
        self.boxesString = []
        start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                global_x, global_y = FuncSerial.getGlobalCoordinates(self.modCounter, x, y)
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], global_x, global_y))
                serString = str(self.classids[i]).encode('utf-8') + str(' ').encode('utf-8') + str(self.modCounter).encode('utf-8') + str(' ').encode('utf-8') + str(round(self.confidences[i],2)).encode('utf-8') + str(' ').encode('utf-8') + str(global_x).encode('utf-8') + str(' ').encode('utf-8') + str(global_y).encode('utf-8') + str('\n').encode('utf-8')
                self.ser.write(serString)
                self.boxesString.append(string)
                #print(x, y)
                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
                
        end = time.time()
        print("drawLabels...() " + str(end - start))

    def counter1():
        print("counter1()")
        self.frame[0:512, 0:512] = self.tile

    def counter2():
        print("counter2()")
        self.frame[0:512, 512:1024] = self.tile

    def counter3():
        #print("counter3()")
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
        #print("counter7()")
        self.frame[512:1024, 1024:1536] = self.tile

    def counter8():
        print("counter8()")
        self.frame[512:1024, 1536:2048] = self.tile

    def counter9():
        print("counter9()")
        self.frame[1024:1536, 0:512] = self.tile

    def counter10():
        #print("counter10()")
        self.frame[1024:1536, 512:1024] = self.tile

    def counter11():
        #print("counter11()")
        self.frame[1024:1536, 1024:1536] = self.tile

    def counter12():
        #print("counter12()")
        self.frame[1024:1536, 1536:2048] = self.tile

    def counter13():
        #print("counter13()")
        self.frame[1536:2048, 0:512] = self.tile

    def counter14():
        #print("counter14()")
        self.frame[1536:2048, 512:1024] = self.tile

    def counter15():
        #print("counter15()")
        self.frame[1536:2048, 1024:1536] = self.tile

    def counter16():
        #print("counter16()")
        self.frame[1536:2048, 1536:2048] = self.tile

    def concatTileAndFrame(self):
        #print("ReaderSeriell.concatTileAndFrame()")

        switch = {
            1: self.counter1,
            2: self.counter2, 
            3: self.counter3,
            4: self.counter4,
            5: self.counter5,
            6: self.counter6,
            7: self.counter7,
            8: self.counter8,
            9: self.counter9,
            10: self.counter10,
            11: self.counter11,
            12: self.counter12,
            13: self.counter13,
            14: self.counter14,
            15: self.counter15,
            0 : self.counter16,
            }
        switch.get(self.modCounter, lambda :  "fail")

    def detectImage(self): 
        #print("Yolo.detectImage()")
        self.modCount()
        self.tile = FuncSerial.getTile(self.modCounter, self.frame)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        self.concatTileAndFrame()
        self.writeList()
        self.display()

    def display(self):
        #print("Mainwindow.display(): ")
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        self.frame = QImage(self.frame, 2048, 2048, QImage.Format_RGB888)
        pixMap = QPixmap.fromImage(self.frame)
        pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixMap) # return pixmapitem
        self.mainWindow.player.setScene(scene)
        QtWidgets.QApplication.processEvents()

    def writeList(self):
        #print("Reader_seriell.writeList()")
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(self.boxesString)

    def getVideo(self):
        #print("load video ...")
        videoName = "videos/12-12-2019 MONO 30fps 11_51_25_Testvideo_10s.avi"
        string = self.mainWindow.console.text() + "load video file ..." + videoName + "\n"
        self.mainWindow.console.setText(string)
        
        cap = cv2.VideoCapture(videoName)
        print("VideoCaptureBackendName: " + cap.getBackendName())
        print("fps: " + str(cap.get(cv2.CAP_PROP_FPS)))
        print("codec: " + str(cap.get(cv2.CAP_PROP_FOURCC)))
        framenumber = 1
        while(cap.isOpened() ): #and self.counter <=5
            if framenumber % 5 == 0:
                framenumber = 1
                ret, self.frame = cap.read()
                if ret == False:
                    break
                self.frameOneGray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
                run_start = time.time()
                self.detectImage()   
                run_end = time.time()
                print("ReaderSeriell.detectImage(): " + str(run_end - run_start))
                string = "ReaderSeriell.detectImage(): " + str(run_end - run_start) + "\n"              
                self.mainWindow.console.setText(self.mainWindow.console.text() + string)               
                #print(str(run_end - run_start))
               # nvof = cv2.cuda_NvidiaOpticalFlow_1_0.create(2048, 2048, 5,
               # False, False, False, 0)
                #flow = nvof.calc(self.frameOneGray, self.frameTwoGray, None)
                #flowUpSampled = nvof.upSampler(flow[0], 2048, 2048,
                #nvof.getGridSize(), None)
                #cv2.writeOpticalFlow('OpticalFlow.flo', flowUpSampled)
                #nvof.collectGarbage()
                self.counter += 1
                QtWidgets.QApplication.processEvents()
            else:
                ret, self.frameTwo = cap.read()
                if ret == False:
                    break
                self.frameTwoGray = cv2.cvtColor(self.frameTwo, cv2.COLOR_RGB2GRAY)
                #self.display()
                framenumber = framenumber + 1
                #print(str(framenumber))
            
        cap.release()
        self.ser.write(b'end of the hunt \n')
        #self.ser.close()