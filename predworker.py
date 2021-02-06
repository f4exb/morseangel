import queue
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import predictions, decoder

class PredictionsWorker(QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal()
    newChar = pyqtSignal(str)

    def __init__(self, preds, dataq):
        super().__init__()
        self.preds = preds
        self.dataq = dataq
        self.running = True
        self.decoder = decoder.MorseDecoderRegen()

    def set_dit_len(self, dit_len):
        self.decoder.set_dit_len(dit_len)

    def set_thr(self, thr):
        self.decoder.set_thr(thr)

    def reset_hist(self):
        self.decoder.reset_hist()

    def run(self):
        while self.running:
            try:
                data = self.dataq.get(timeout=1) # give a chance to stop thread
            except queue.Empty:
                continue
            self.preds.new_data(data)
            if self.preds.p_preds_t is not None:
                self.dataReady.emit()
                for i in range(self.preds.p_preds_t.shape[1]):
                    s = self.preds.p_preds_t[:,i]
                    char, env = self.decoder.new_sample(s)
                    if char:
                        self.newChar.emit(self.decoder.char)
        self.finished.emit()
