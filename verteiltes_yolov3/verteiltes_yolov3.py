import mainwindow
import sys
from PyQt5.QtGui import QPixmap
# funktionierende Config auf Workstation:
# Python 3.7.4
# OpenCV 4.4.0
# CUDA 10.0
# cuDNN 7.5.1
#
#
#

from PyQt5 import QtWidgets, QtCore, uic


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pixmap = QPixmap("C:/Insektenlaser/GIT/verteiltes_yolov3/verteiltes_yolov3/icons/LogoFinalOhneHaus.png")
    splash = QtWidgets.QSplashScreen(pixmap.scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation))
    splash.show()
    #app.processEvents()
    mainWindow = mainwindow.Window()
    mainWindow.show()
    mainWindow.start()
    splash.finish(mainWindow)
    app.exec_()
    