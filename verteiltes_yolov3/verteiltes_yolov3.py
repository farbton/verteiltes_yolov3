#! D:\Insektenlaser\Anaconda3\envs\verteiltesYolo

import gui
import sys
from PyQt5 import QtWidgets, uic

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = gui.Window()
    w.show()
    w.refresh_button.clicked.connect(lambda: w.label_write())   
    app.exec_()
    
if __name__ == "__main__":
    main()