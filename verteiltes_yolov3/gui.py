import sys
from PyQt5 import QtWidgets, uic

class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Viewer for Yolov3")

    def label_write(self):
        self.label.setText("hallo")
        return

    #def refresh_graphicView_image(self, pix_map_item):
    #    scene = QtWidgets.QGraphicsScene()
    #    scene.addItem(pix_map_item)
    #    self.graphicsView.setScene(scene)
    #    return

