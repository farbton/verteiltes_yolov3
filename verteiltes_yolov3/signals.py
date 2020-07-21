from PyQt5.QtGui import QImage
from PyQt5.QtCore import pyqtSignal, QObject


class WorkerSignals(QObject):

    output_signal = pyqtSignal(QImage)
