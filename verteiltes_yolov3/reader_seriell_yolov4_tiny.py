from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import numpy as np
import serial
#from functions import FuncSerial
import functions

class ReaderSeriellTiny(QtCore.QObject):
    def __init__(self, mainWindow):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        #self.cfgFileName = "yolo/yolov3.cfg" 
        #self.weightsFile = "yolo/yolov3_512.weights" 
        #self.cfgFileName = "yolo/yolov4-obj.cfg" 
        #self.weightsFile = "yolo/yolov4-obj_best.weights"
        self.cfgFileName = "yolo/yolov4-tiny-kirko.cfg" 
        self.weightsFile = "yolo/yolov4-tiny-kirko_best.weights"
        self.classesFile = "yolo/weevil.names"
        self.ser = serial.Serial('COM4', 115200)
        print("Serialname: " , self.ser.name)
        time.sleep(2)
        #self.ser.write('weevil hunter\'s eye \n'.encode('utf-8'))
        self.ser.write(b'cls quad conf x y \n')
        self.ser.flush()
        sString = "COM-Port: " + self.ser.name + "\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
        strich = "========================================================\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + strich)
        self.imageHeight = 512
        self.imageWidth = 512
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
        self.modCounter = self.counter % 16
   
    def createBlob(self):
        #print("ReaderSeriell.createBlob()")
        #start = time.time()
        self.blob = cv2.dnn.blobFromImage(self.tile, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        #end = time.time()
        #print("createBlob(): " + str(end - start))

    def setNetInput(self):
        #print("ReaderSeriell.setNetInput()")
        #start = time.time()
        self.net.setInput(self.blob)        
        #end = time.time()
        #print("setNetInput(): " + str(end - start))

    def getOutput(self):
        #print("ReaderSeriell.getOutput()")
        #start = time.time()
        self.outs = self.net.forward(self.layerNames)
        #end = time.time()
        #print("getOutput(): " + str(end - start))

    def generateBoxes_confidences_classids(self):
        #print("ReaderSeriell.generateBoxes_confidence_classids()")
        #start = time.time()
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

        #end = time.time()
        #print("generate_boxes...() " + str(end - start))

    def printBoxes(self):
        pass
        #self.mainWindow.listWidget.addItems(self.boxes)

    def nonMaximaSupress(self):
        #print("Yolo.nonMaximaSupress()")
        #start = time.time()
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)
        #end = time.time()
        #print("nonMaximaSupress() " + str(end - start))

    def drawLabelsAndBoxes(self):
        #print("Yolo.drawLabelsAndBoxes()")
        self.boxesString = []
        #start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                global_x, global_y = functions.getGlobalCoordinates(self.modCounter, x, y)
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], global_x, global_y))
                #serString = str(self.classids[i]).encode('utf-8') + str(' ').encode('utf-8') \
                #          + str(self.modCounter).encode('utf-8') + str(' ').encode('utf-8') \
                #          + str(round(self.confidences[i],2)).encode('utf-8') +str(' ').encode('utf-8') \
                #          + str(global_x).encode('utf-8') + str(' ').encode('utf-8') \
                #          + str(global_y).encode('utf-8') + str(' ').encode('utf-8') \
                #          + str('\n').encode('utf-8')
                serString = str(global_x).encode('utf-8') + str(' ').encode('utf-8') \
                          + str(global_y).encode('utf-8') + str(' ').encode('utf-8') \
                          + str('\n').encode('utf-8')
                self.ser.write(serString)
                #print(string)
                #self.ser.flush()
                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes
                self.boxesString.append(string) 
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
                
        #end = time.time()
        #print("drawLabels...() " + str(end - start))

    def drawLabelsAndBoxesImage(self):
        #print("Yolo.drawLabelsAndBoxes()")
        self.boxesString = []
        #start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                string = ("{:3.2f}, {:4d}, {:4d}".format(self.confidences[i], x, y))
                #serString = str(self.classids[i]).encode('utf-8') + str('
                #').encode('utf-8') + str(self.modCounter).encode('utf-8') +
                #str(' ').encode('utf-8') +
                #str(round(self.confidences[i],2)).encode('utf-8') + str('
                #').encode('utf-8') + str(global_x).encode('utf-8') + str('
                #').encode('utf-8') + str(global_y).encode('utf-8') +
                #str('\n').encode('utf-8')
                #self.ser.write(serString)
                self.boxesString.append(string)
                #print(x, y)
                #color = [int(c) for c in self.colors[self.classids[i]]] # for
                #more classes
                cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
                
        #end = time.time()
        #print("drawLabels...() " + str(end - start))

    def detectImage(self): 
        #print("Yolo.detectImage()")
        self.modCount()
        self.tile = functions.getTile(self.modCounter, self.frame)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        self.frame = functions.concatTileAndFrame(self.modCounter,self.frame, self.tile)
        #cv2.imshow("test2", self.frameConcat)
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
        self.end_time = time.time()
        self.oneCycleList.append(self.end_time - self.begin_time)
        #print("ser_oneCycle: " + str(round(self.end_time - self.begin_time,3)) + " netTime: " + str(round(self.netTime,3)))

    def writeList(self):
        #print("Reader_seriell.writeList()")
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(self.boxesString)

    def getVideo(self):
        #print("load video ...")
        videoName = "videos/12-12-2019 MONO 30fps 11_51_25_Testvideo_10s.avi" 
        #videoName = "videos/12-12-2019 MONO 30fps 11_49_58_Kaefer auf
        #Korn_4800mikros.avi"
        string = self.mainWindow.console.text() + "load video file ..." + videoName + "\n"
        self.mainWindow.console.setText(string)
        
        cap = cv2.VideoCapture(videoName)
        print("VideoCaptureBackendName: " + cap.getBackendName())
        print("fps: " + str(cap.get(cv2.CAP_PROP_FPS)))
        print("codec: " + str(cap.get(cv2.CAP_PROP_FOURCC)))
        framenumber = 1
        starttime = time.time()
        while(cap.isOpened() ): # and self.counter <=1
           # if framenumber % 2 == 0:
            framenumber = 1
            self.begin_time = time.time()
            ret, self.frame = cap.read()
            if ret == False:
                break
            #self.frameOneGray = cv2.cvtColor(self.frame,
            #cv2.COLOR_RGB2GRAY)
            run_start = time.time()
            self.detectImage()   
            run_end = time.time()
            self.netTime = run_end - run_start
            self.netTimeList.append(self.netTime)
            #print("ReaderSeriell.detectImage(): " + str(run_end -
            #run_start))
            #string = "ReaderSeriell.detectImage(): " + str(round(run_end -
            #run_start,4)) + "\n"
            #self.mainWindow.console.setText(self.mainWindow.console.text()
            #+ string)
            #self.mainWindow.scrollArea.verticalScrollBar().setValue(self.mainWindow.scrollArea.verticalScrollBar().maximum())
            #self.mainWindow.scrollArea.verticalScrollBar().setSliderDown(True)
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
          # else:
          #      ret, self.frameTwo = cap.read()
          #      if ret == False:
          #          break
                #self.frameTwoGray = cv2.cvtColor(self.frameTwo,
                #cv2.COLOR_RGB2GRAY)
                #self.display()
          #      framenumber = framenumber + 1
                #print(str(framenumber))
            
        cap.release()
        self.ser.write(b'end of hunt \n')
        endtime = time.time()
        #avgCyle = round(sum(self.oneCycleList[2:]) / len(self.oneCycleList[2:]),3)
        #avgNetTime = round(sum(self.netTimeList[2:]) / len(self.netTimeList[2:]),3)
        #print("(tinyV4)ser_avg_CycleTime: " + str(avgCyle) + " avg_TinyV4NetTime: " + str(avgNetTime))
        print(str(endtime - starttime))
        self.ser.close()

    def getImage(self, filename):
        self.tile = cv2.imread(filename)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxesImage()
        self.writeList()
        return self.tile
