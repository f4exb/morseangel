from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("My Awesome App")

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(Color('red'))

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setGeometry(100, 100, 800, 300)
        self.setWindowTitle('MorseAngel')
        self.show()
