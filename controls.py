from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

class ControlWidget(QtWidgets.QWidget):

    wpmSignal = pyqtSignal(int)
    thrSignal = pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super(ControlWidget, self).__init__(*args, **kwargs)
        vbox = QtWidgets.QVBoxLayout()
        # line 1
        hl1 = QtWidgets.QHBoxLayout()
        self.wpmLabel = QtWidgets.QLabel(self)
        self.wpmLabel.setText("WPM")
        self.wpm = QtWidgets.QSlider(Qt.Horizontal)
        self.wpm.setMinimum(1)
        self.wpm.setMaximum(40)
        self.wpm.setSingleStep(1)
        self.wpm.setPageStep(1)
        self.wpm.setValue(17)
        self.wpm.valueChanged.connect(self.wpmChange)
        self.wpmText = QtWidgets.QLabel(self)
        self.wpmText.setText("17")
        hl1.addWidget(self.wpmLabel)
        hl1.addWidget(self.wpm)
        hl1.addWidget(self.wpmText)
        hl1_widget = QtWidgets.QWidget()
        hl1_widget.setLayout(hl1)
        # line 2
        hl2 = QtWidgets.QHBoxLayout()
        self.thrLabel = QtWidgets.QLabel(self)
        self.thrLabel.setText("Thr")
        self.thr = QtWidgets.QSlider(Qt.Horizontal)
        self.thr.setMinimum(-50)
        self.thr.setMaximum(0)
        self.thr.setSingleStep(1)
        self.thr.setPageStep(1)
        self.thr.setValue(-30)
        self.thr.valueChanged.connect(self.thrChange)
        self.thrText = QtWidgets.QLabel(self)
        self.thrText.setText("-30")
        hl2.addWidget(self.thrLabel)
        hl2.addWidget(self.thr)
        hl2.addWidget(self.thrText)
        hl2_widget = QtWidgets.QWidget()
        hl2_widget.setLayout(hl2)
        # vbox
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(hl1_widget)
        self.vbox.addWidget(hl2_widget)
        self.setLayout(self.vbox)

    def wpmChange(self):
        wpm = self.wpm.value()
        self.wpmText.setText(str(wpm))
        self.wpmSignal.emit(wpm)

    def thrChange(self):
        thr_dB = self.thr.value()
        thr = 10**(thr_dB/10.0)
        self.thrText.setText(str(thr_dB))
        self.thrSignal.emit(thr)
