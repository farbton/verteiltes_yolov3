import gui
import sys
from reader import Reader 

from PyQt5 import QtWidgets, uic

def start():        
    mainWindow.refresh_button.clicked.connect(mainWindow.label_write)
    mainWindow.actionload_image.triggered.connect(reader.read_image)
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = gui.Window()
    mainWindow.show()
    reader = Reader(mainWindow)
    start()
    app.exec_()
    