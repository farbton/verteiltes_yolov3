import mainwindow
import sys
# funktionierende Config auf Workstation:
# Python 3.7.4
# OpenCV 4.4
# CUDA 10.0
# cuDNN 7.5.1
#
#
#

from PyQt5 import QtWidgets, uic


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = mainwindow.Window()
    mainWindow.show()
    mainWindow.start()
    app.exec_()
    