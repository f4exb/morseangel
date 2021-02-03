import queue
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import predictions

class PredictionsWorker(QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal()

    def __init__(self, preds, dataq):
        super().__init__()
        self.preds = preds
        self.dataq = dataq
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.dataq.get(timeout=1) # give a chance to stop thread
            except queue.Empty:
                continue
            self.preds.new_data(data)
            if self.preds.p_preds_t is not None:
                self.dataReady.emit()
        self.finished.emit()
