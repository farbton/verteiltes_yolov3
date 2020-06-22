import sys
from PyQt5 import QtWidgets, uic

class Window(QtWidgets.QMainWindow):
    
    def __init__(self):       
        super(Window, self).__init__()       
        uic.loadUi("gui.ui", self)


    def label_write(self):
        self.label.setText("hallo")
        return




#w.connect(w.refresh_button, SIGNAL("clicked()"),  w.label_write())

