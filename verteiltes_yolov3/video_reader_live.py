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
            self.ser = serial.Serial('COM3', 9600)
            self.ser.write(b'hello here is the weevil hunter\'s eye \n')
            self.ser.write(b'class quadrant confidence x y \n')
            sString = "COM-Port: " + self.ser.name + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
        except:
            sString = "no COM-Port avalible \n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + sString)

        time.sleep(2)
        
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
        
        self.boardThread = siso_board.SisoBoard(self.mainWindow)   
        self.boardThread.signals.live_image.connect(self.detectImage)
        #self.boardThread.finished.connect(self.test)
        self.boardThread.run()
            
    def test(self):
        print("fertig")


    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFileName, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def readNet(self):
        #print("Reader.readNet()")
        string = self.mainWindow.console.text() + "reader_seriell read net ...  "
        self.mainWindow.console.setText(string)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFileName)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        #print(self.net)

    def setLayerNames(self):
        #print("Reader.setLayerNames()")
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        #print(self.layerNames)
        #print(self.net.dump())

    def modCount(self):
        self.modCounter = self.counter % 16
        self.counter += 1
        #print("modCounter: ", self.modCounter)
   
    def createBlob(self):
        #print("VideoReaderLive.createBlob()")
        #start = time.time()
       # print("tile.shape: ", self.tile.shape)
        
        self.blob = cv2.dnn.blobFromImage(self.tile, 1/255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        #end = time.time()
        #print(self.blob)
        #print("createBlob(): " + str(end - start))

    def setNetInput(self):
        #print("VideoReaderLive.setNetInput()")
        #start = time.time()
        self.net.setInput(self.blob)        
        #end = time.time()
        #print("setNetInput(): " + str(end - start))

    def getOutput(self):
        #print("VideoReaderLive.getOutput()")
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
        self.detections = 0
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
                self.detections = len(self.idxs)
        else:
            #cv2.rectangle(self.tile, (x,y), (x + w, y + h), (255,0,0), 2)
            #cv2.putText(self.tile, "X", (256, 256), cv2.FONT_HERSHEY_SIMPLEX, 5, (255,0,0))
            pass
        #end = time.time()
        #print("drawLabels...() " + str(end - start))
 
    #@QtCore.pyqtSlot(np.ndarray)
    def detectImage(self, ndarray): 
        #print("ndarray.shape: ",ndarray.shape)
        #cv2.imshow("test", ndarray )
        #cv2.waitKey(0)
        frame3d = np.ndarray((2048, 2048, 3), dtype=np.uint8)
        
        frame3d[:,:,0] = ndarray
        frame3d[:,:,1] = ndarray
        frame3d[:,:,2] = ndarray
        #cv2.imshow("test", frame3d )
        #cv2.waitKey(0)
        self.modCount()
        self.tile = functions.getTile(self.modCounter, frame3d)
        #print("tile.shape: ",self.tile.shape)
        #print("tile.dtype: ",self.tile.dtype)
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        self.nonMaximaSupress()
        #cv2.imshow("test", self.tile )
        #cv2.waitKey(0)
        self.drawLabelsAndBoxes()
        self.frame = functions.concatTileAndFrame(self.modCounter, frame3d, self.tile)
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
        dString = "detections: " + str(self.detections) + " \n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + dString)
        self.autoscroll()
        #self.oneCycleList.append(self.end_time - self.begin_time)
        #print("ser_oneCycle: " + str(round(self.end_time - self.begin_time,3)) + " netTime: " + str(round(self.netTime,3)))

    #@QtCore.pyqtSlot(QImage)
    #def display(self, qimage):
    #    #self.mutexDislpay.lock()
    #    #print("reader_parallel.display(): ")
    #    height = self.mainWindow.player.geometry().height()
    #    width = self.mainWindow.player.geometry().width()
    #    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #    #frameImage = QImage(frame.data, frame.shape[1], frame.shape[0],
    #    #QImage.Format_RGB888)
    #    pixMap = QPixmap.fromImage(qimage)
    #    pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
    #    scene = QtWidgets.QGraphicsScene()
    #    scene.addPixmap(pixMap) # return pixmapitem
    #    self.mainWindow.player.setScene(scene)
    #    #self.mutexDislpay.unlock()
    #    #self.end_time = time.time()
    #    #cycle = round(self.end_time-self.begin_time,3)
    #    #self.oneCycleList.append(cycle)
    #    #print("paral_oneCycle: " + str(cycle) + " thread: " + str(round(self.threadTime,3)))
    #    #self.mainWindow.console.clear()       
    #    QtWidgets.QApplication.processEvents()

    def writeList(self):
        #print("Reader_seriell.writeList()")
        self.mainWindow.listWidget.clear()
        self.mainWindow.listWidget.addItems(self.boxesString)

    def autoscroll(self):
        self.mainWindow.scrollArea.verticalScrollBar().setValue(self.mainWindow.scrollArea.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()

    
