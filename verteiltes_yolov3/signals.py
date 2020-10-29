from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np

class WorkerSignals(QObject):

    #output_signal = pyqtSignal(QImage)
    #signal_detectionList = pyqtSignal(list)
    live_image = pyqtSignal(np.ndarray) #von siso.board nach video_reader_live
