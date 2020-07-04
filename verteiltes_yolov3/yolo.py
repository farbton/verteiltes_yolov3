import numpy as np
import cv2
import time

class Yolo(object):
    """description of class"""
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.cfgFileName = "yolo/yolov3.cfg" 
        self.weightsFile = "yolo/yolov3_512.weights"
        self.classesFile = "yolo/weevil.names"
        self.imageHeight = 512
        self.imageWidth = 512
        self.conf_threshhold = 0.5 
        self.nms_treshold = 0.5
        self.orgSize = 2048
        self.prepareYolo()

    def autoscroll(self):
        print("yolo.autoscroll()")
        print("yolo...maximum(): ", self.mainWindow.scrollArea.verticalScrollBar().maximum())
        self.mainWindow.scrollArea.verticalScrollBar().setValue(self.mainWindow.scrollArea.verticalScrollBar().maximum())

    def loadModel(self):
        pass

    def loadWeights(self):
        pass

    def detectFrame(self):
        pass

    def prepareYolo(self):
        self.getClassesNames()
        self.printClassesNames()
        #self.setColors()
        self.readNet()
        self.setLayerNames()

    def detectImage(self):       
        self.createBlob()
        self.setNetInput()
        self.getOutput()
        self.generateBoxes_confidences_classids()
        #self.printBoxes()
        self.nonMaximaSupress()
        self.drawLabelsAndBoxes()
        return self.image

    def getClassesNames(self):        
        self.classes = None
        with open(self.classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def printClassesNames(self):
        self.mainWindow.listWidget.addItems(self.classes)

    #def setColors(self):
    #    self.colors = np.random.randint(0, 255, size=(len(self.classes), 3),
    #    dtype='uint8')

    def readNet(self):
        string = self.mainWindow.console.text() + "read net ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #self.autoscroll()
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.cfgFileName,self.weightsFile)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #self.autoscroll()

    def setLayerNames(self):
        self.layerNames = self.net.getLayerNames()
        self.layerNames = [self.layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        print(self.layerNames)
        
    def createBlob(self):
        #image_name = "images/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros0.jpg"
        image_name = "images_512/12-12-2019 MONO 30fps 11_33_48_Kaefer auf Korn_4200mikros840_rot90sub1.jpg"
        dim = (512, 512)
        string = self.mainWindow.console.text() + "create blob ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        start = time.time()
        self.image = cv2.imread(image_name)
        resized = cv2.resize(self.image, dim, interpolation = cv2.INTER_AREA)
        self.blob = cv2.dnn.blobFromImage(resized, 1 / 255, (self.imageHeight, self.imageWidth), [0,0,0], 1, crop=False)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def setNetInput(self):
        string = self.mainWindow.console.text() + "set netinput ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #self.autoscroll()
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
        #self.autoscroll()
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
        #self.autoscroll()
        start = time.time()
        self.boxes = []
        self.confidences = []
        self.classids = []

        for out in self.outs:
            for detection in out:

                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]

                if confidence > 0.6:
                    box = detection[0:4] * np.array([self.imageWidth, self.imageHeight, self.imageWidth, self.imageHeight])
                    centerX, centerY, bwidth, bheight = box.astype('int')
                
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    string = ("{:3.2f}, {:5d}, {:4d}, {:4d}, {:4d}".format(confidence, x, y, int(bwidth), int(bheight)))

                    self.mainWindow.listWidget.addItem(string)
                    self.mainWindow.listWidget.repaint()
                    self.mainWindow.repaint()
                    self.boxes.append([x,y, int(bwidth), int(bheight)])
                    self.confidences.append(float(confidence))
                    self.classids.append(classid)
                    #print("length: " + str(len(self.confidences)))

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
        #self.autoscroll()
        start = time.time()
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.conf_threshhold, self.nms_treshold)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()

    def drawLabelsAndBoxes(self):
        #print("drawLabelsAndBoxes(self)")
        string = self.mainWindow.console.text() + "draw Labels and Boxes ... "
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #self.autoscroll()
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
                cv2.rectangle(self.image, (x,y), (x + w, y + h), (0,0,255), 2)
                #text = "{}: {:4f}".format(self.classes[self.classids[i]],
                #self.confidences[i])
                #cv2.putText(self.image, text, (x, y - 5),
                #cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
                
                #self.imageToPixmap()
                #self.setConsoleHeightWidth()
                #self.resizePixmap()
                #self.pixmapSetScene()
                #self.addSceneToPlayer()
            #self.showImage()
            if len(self.idxs.flatten()) > 0:
                string = self.mainWindow.console.text() + "%3d detections in " % len(self.idxs.flatten())
                self.mainWindow.console.setText(string)
        end = time.time()
        string = self.mainWindow.console.text() + "{:2f} s \n".format(end - start)
        self.mainWindow.console.setText(string)
        self.mainWindow.console.repaint()
        #self.autoscroll()

    def showImage(self):
        img = cv2.resize(self.image, (1500, 1500))
        cv2.imshow('Image', img)
        cv2.resizeWindow('Image', 1500, 1500)
        #cv2.waitKey(0)

    