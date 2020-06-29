import numpy as np
import os
import cv2
import time
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtWidgets
from PyQt5 import QtCore 

class Reader(object):
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.cfgFileName = "yolo/yolov3.cfg" 
        self.weightsFile = "yolo/yolov3.weights"
        self.imageHeight = 2048
        self.imageWidth = 2048
        #pass

    def addSceneToPlayer(self):
        self.mainWindow.player.setScene(self.scene)

    def getImage(self):
        print("getImage(self, height, width)")
        self.setConsoleHeightWidth()
        self.loadImage()
        self.imageToPixmap()
        # Abgriff der pixmap zur Verarbeitung im CNN
        self.resizePixmap()
        self.pixmapSetScene()
        self.addSceneToPlayer()
        #return self.scene
    

    def loadYolofromDarknet(self):
        self.getClassesNames()
        self.printClassesNames()
        self.setColors()
        self.readNet()
        self.setLayerNames()
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        #self.printBoxes()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        #os.system("PAUSE")

    def getClassesNames(self):
        classesFile = "yolo/weevil.names"
        self.classes = None
        with open(classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def printClassesNames(self):
        self.mainWindow.listWidget.addItems(self.classes)


    def setColors(self):
        self.colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype='uint8')


    def readNet(self):
        string = self.mainWindow.console.text() + "read net ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFile)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def setLayerNames(self):
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        print(self.layerNames)
        
    def createBlob(self):
        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"        
        string = self.mainWindow.console.text() + "create blob ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.image = cv2.imread(image_name)
        self.blob = cv2.dnn.blobFromImage(self.image, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def setNetInput(self):
        string = self.mainWindow.console.text() + "set netinput ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.net.setInput(self.blob)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def getOutput(self):
        string = self.mainWindow.console.text() + "get output ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.outs = self.net.forward(self.layerNames)
        end = time.time()
        string = self.mainWindow.console.text() + "{:6f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #print(self.outs)
        #self.mainWindow.console.additems(self.outs)

    def generateBoxes_confidences_classids(self):
        string = self.mainWindow.console.text() + "generateBoxes, confidences and classids ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.boxes = []
        self.confidences = []
        self.classids = []

        for out in self.outs:
            for detection in out:

                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]

                if confidence > 0.3:
                   # print("scores:", scores)
                   # print("classId:", classid)
                   # print("confidence:", confidence)
                    box = detection[0:4] * np.array([self.imageWidth, self.imageHeight, self.imageWidth, self.imageHeight])
                    centerX, centerY, bwidth, bheight = box.astype('int')
                
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    string = ("{:3.2f}, {:4d}, {:4d}, {:4d}, {:4d}".format(confidence, x, y, int(bwidth), int(bheight)))
                    #string = ("%3.2f, %4d, %4i, %i, %i" % (confidence, x, y, int(bwidth), int(bheight)))
                    self.mainWindow.listWidget.addItem(string)
                    self.mainWindow.listWidget.repaint()
                    self.mainWindow.repaint()
                    self.boxes.append([x,y, int(bwidth), int(bheight)])
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)

        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()


    def printBoxes(self):
        self.mainWindow.listWidget.addItems(self.boxes)

    def nonMaximaSupress(self):
        #print("nonMaximaSupress(self)")
        string = self.mainWindow.console.text() + "nonMaximaSupress ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, 0.2, 0.2)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def drawLabelsAndBoxes(self):
        print("drawLabelsAndBoxes(self)")
        string = self.mainWindow.console.text() + "draw Labels and Boxes ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        if len(self.idxs) > 0:
            for i in self.idxs.flatten():
                x, y = self.boxes[i][0], self.boxes[i][1]
                w, h = self.boxes[i][2], self.boxes[i][3]
                color = [int(c) for c in self.colors[self.classids[i]]]
                cv2.rectangle(self.image, (x,y), (x + w, y + h), color, 2)
                text = "{}: {:4f}".format(self.classes[self.classids[i]], self.confidences[i])
                cv2.putText(self.image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color,2)
                
                #self.imageToPixmap()
                #self.setConsoleHeightWidth()
                #self.resizePixmap()
                #self.pixmapSetScene()
                #self.addSceneToPlayer()
            self.showImage()
            if len(self.idxs.flatten()) > 0:
                string = self.mainWindow.console.text() + "%3d detections in " % len(self.idxs.flatten())
                self.mainWindow.console.setText(string)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        
        self.mainWindow.console.repaint()

    def showImage(self):
        img = cv2.resize(self.image, (1000, 1000))
        cv2.imshow('Image', img)
        cv2.resizeWindow('Image', 1000, 1000)
        #cv2.waitKey(0)

    def setConsoleHeightWidth(self):
        self.consoleHeight = self.mainWindow.player.geometry().height()
        self.consoleWidth = self.mainWindow.player.geometry().width()
    
    def loadImage(self):
        image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        string = self.mainWindow.console.text() + "load image file ..." + image_name + "\n"
        self.mainWindow.console.setText(string)
        #self.image = cv2.imread(image_name)
        self.image = QImage(image_name)

    def imageToPixmap(self):
        self.pixMap = QPixmap(QImage(self.image, 416, 416, QImage.Format_RGB888))

    def resizePixmap(self):
        self.pixMap = self.pixMap.scaled(QtCore.QSize(self.consoleHeight, self.consoleWidth), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
    
    def pixmapSetScene(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.pixMap) # return pixmapitem

    def getVideo(self):
        print("load video ...")       
        videoName = "videos/YOLOv3_output_29.05.2020_10s.avi"
        height = self.mainWindow.player.geometry().height()
        width = self.mainWindow.player.geometry().width()
        cap = cv2.VideoCapture(videoName)
        #timer = QtCore.QTimer()
        while(cap.isOpened()):
            ret,frame = cap.read()
            #self.mainWindow.statusBar().showMessage(timer.remainingTime())
            #print(timer.remainingTime())
            if ret == False:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frameImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixMap = QPixmap.fromImage(frameImage)
            pixMap = pixMap.scaled(QtCore.QSize(height, width), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            scene = QtWidgets.QGraphicsScene()
            scene.addPixmap(pixMap) # return pixmapitem
            self.mainWindow.player.setScene(scene)
            QtWidgets.QApplication.processEvents()
        