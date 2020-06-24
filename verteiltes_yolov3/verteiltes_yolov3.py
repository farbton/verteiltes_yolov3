import mainwindow
import sys
 

from PyQt5 import QtWidgets, uic


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = mainwindow.Window()
    mainWindow.show()
    mainWindow.start()
    app.exec_()
    