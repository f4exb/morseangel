import os, sys
import queue
from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia
from PyQt5.QtGui import QPalette, QColor, QTextCursor
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import periodogram, spectrogram
import audiodialog, controls, predictions, predworker
sys.path.append('./notebooks')
from peakdetect import peakdet


def get_audioin_devices():
    return QtMultimedia.QAudioDeviceInfo.availableDevices(QtMultimedia.QAudio.AudioInput)

def print_devices(devices):
    for device in devices:
        print(device.deviceName(), device.supportedSampleRates())

def specimg(Fs, signal, tone, nfft, noverlap, wbins, complex=False):
    """ Create spectral image around tone frequency
    """
    nperseg = nfft if nfft < 256 or noverlap >= 256 else 256
    f, t, Sxx = spectrogram(signal, Fs, nfft=nfft, noverlap=noverlap, nperseg=nperseg, scaling='density')
    fbin = (tone/(Fs/2))* (len(f)-1)
    if complex:
        fbin /= 2
    center_bin = int(round(fbin))
    return f[center_bin-wbins:center_bin+wbins+1], t, Sxx[center_bin-wbins:center_bin+wbins+1,:]

def nb_samples_per_dit_decim(Fs=8000, code_speed=13, decim=7.69):
    """ One dit of time at w wpm is 1.2/w.
        Returns a tuple (raw samples per dit, expected decimation factor)
        Overlap is nfft - decimation factor
    """
    t_dit = 1.2 / code_speed
    return int(t_dit * Fs), int(t_dit * Fs) / decim

def fft_optim(Fs=8000, code_speed=13, decim=7.69):
    spd, fft_decim = nb_samples_per_dit_decim(Fs, code_speed, decim)
    log2_spd = np.log(spd) / np.log(2)
    nfft = 2**int(log2_spd-1)
    noverlap = nfft - round(fft_decim)
    return nfft, noverlap

def make_palette():
    """ Make theme like SDRangel's
    """
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53,53,53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25,25,25))
    palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(0x40, 0x40, 0x40))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Light, QColor(53,53,53).lighter(125).lighter())
    palette.setColor(QPalette.Mid, QColor(53,53,53).lighter(125))
    palette.setColor(QPalette.Dark, QColor(53,53,53).lighter(125).darker())
    palette.setColor(QPalette.Link, QColor(0,0xa0,0xa0))
    palette.setColor(QPalette.LinkVisited, QColor(0,0xa0,0xa0).lighter())
    palette.setColor(QPalette.Highlight, QColor(0xff, 0x8c, 0x00))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette


class MplTimeCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both', color="gray", alpha=0.8)
        self.axes.set_xlabel(u'samples')
        self.fig.tight_layout(pad=1)
        self.time_line = None
        self.zline0 = None
        self.zline1 = None
        super(MplTimeCanvas, self).__init__(self.fig)

    def set_mp(self, nsamples):
        self.time_vect = np.arange(nsamples)
        self.axes.set_ylim(-1, 1)
        self.axes.set_xlim(0, nsamples)
        if self.time_line:
            while (len(self.axes.lines) > 0):
                self.axes.lines.pop(0)
        self.zline0 = None
        self.zline1 = None
        self.time_line, = self.axes.plot(self.time_vect, np.ones_like(self.time_vect)/2, color="yellow", alpha=0.8)
        self.draw()

    def new_data(self, data, zoom_span=0):
        plotdata = self.time_line.get_data()[1]
        nb_samples = len(data)
        plotdata = np.roll(plotdata, -nb_samples, axis=0)
        plotdata[-nb_samples:] = data
        ymin = min(data)
        ymax = max(data)
        self.axes.set_ylim(ymin*1.2, ymax*1.2)
        self.time_line.set_data(self.time_vect, plotdata)
        if zoom_span:
            if self.zline0:
                self.zline0.remove()
            if self.zline1:
                self.zline1.remove()
            x0 = len(plotdata) - nb_samples
            x1 = x0 + zoom_span
            l0 = mlines.Line2D([x0,x0], [ymin,ymax], color="red")
            l1 = mlines.Line2D([x1,x1], [ymin,ymax], color="red")
            self.zline0 = self.axes.add_line(l0)
            self.zline1 = self.axes.add_line(l1)
        self.draw()


class MplPredCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both', color="gray", alpha=0.8)
        self.axes.set_ylim(0, 3)
        self.fig.tight_layout(pad=1)
        self.colors = ["yellow", "lime", "lightsalmon", "lime", "lightsalmon", "cornflowerblue", "yellow", "fuchsia"]
        super(MplPredCanvas, self).__init__(self.fig)

    def set_mp(self, nsamples, max_ele=5):
        self.nsamples = nsamples
        self.max_ele = max_ele
        self.lines = np.zeros((max_ele+3, nsamples))
        self.labels = ["in", "cs", "ws"]
        for i in range(max_ele):
            self.labels.append(f"e{i}")
        self.axes.set_xlim(0, nsamples)

    def new_data(self, in_data, pred_data):
        self.lines[0] = np.roll(self.lines[0], -len(in_data), axis=0)
        self.lines[0][-len(in_data):] = in_data
        xmax = len(pred_data[0])
        for i in range(1, self.max_ele+3):
            self.lines[i] = np.roll(self.lines[i], -xmax, axis=0)
            self.lines[i][-xmax:] = pred_data[i-1]
        while (len(self.axes.lines) > 0):
            self.axes.lines.pop(0)
        for i in range(self.max_ele+3):
            if i == 0:
                y = 0
            elif i < 3:
                y = 1
            else:
                y = 2
            self.axes.plot(self.lines[i]*0.9 + y, label=self.labels[i], color=self.colors[i], alpha=0.8)
        self.axes.legend(bbox_to_anchor=(-0.1, 1.1), loc='upper left')
        self.draw()


class MplPeakCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both', color="gray")
        self.axes.set_xlabel(u'F (Hz)')
        self.axes.set_ylabel(u'Amplitude (log)')
        self.axes.set_yscale('log')
        self.fig.tight_layout(pad=1)
        self.spec_line = None
        super(MplPeakCanvas, self).__init__(self.fig)

    def set_mp(self):
        if self.spec_line:
            self.axes.lines.pop(0)
        self.spec_line = None

    def new_data(self, f, s, maxtab, tone):
        if not self.spec_line:
            self.spec_line, = self.axes.plot(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]),'g-', color="lime", alpha=0.8)
        else:
            self.spec_line.set_data(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]))
        pmax = max(s)
        self.axes.set_ylim(1e-5, pmax)
        self.axes.set_xlabel(f'F (Hz) \u2191 {tone:9.5f} ({10*np.log10(pmax):5.2f} dB)')
        #self.fig.suptitle(f"Signal peak {10*np.log10(pmax):5.2f} dB found at {tone:9.5f} Hz")
        self.draw()


class MplHistCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=150):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both', color="gray")
        self.ylim = 50
        self.xlim = 40
        self.axes.set_ylim(0, self.ylim)
        self.axes.set_xlim(0, self.xlim)
        lditl = mlines.Line2D([11,11], [0,self.ylim], color="red", linestyle="--")
        ldits = mlines.Line2D([17,17], [0,self.ylim], color="red")
        ldith = mlines.Line2D([23,23], [0,self.ylim], color="red", linestyle="--")
        ldahl = mlines.Line2D([25,25], [0,self.ylim], color="yellow", linestyle="--")
        ldahs = mlines.Line2D([32,32], [0,self.ylim], color="yellow")
        self.axes.add_line(lditl)
        self.axes.add_line(ldits)
        self.axes.add_line(ldith)
        self.axes.add_line(ldahl)
        self.axes.add_line(ldahs)
        self.fig.tight_layout(pad=1)
        self.hbars = None
        super(MplHistCanvas, self).__init__(self.fig)

    def new_data(self, his):
        max_his = int(max(his)) + 1
        if self.hbars:
            t = [b.remove() for b in self.hbars]
        self.hcounts, self.hbins, self.hbars = self.hist = self.axes.hist(his, bins=max_his, color="lightskyblue")
        self.draw()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.audio_devices = get_audioin_devices()
        self.audio_device = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        self.audio_rates = self.audio_device.supportedSampleRates()
        self.audio_rate = self.audio_rates[len(self.audio_rates)-1]
        self.audio_input = None
        self.audio_buffer = None
        self.audio_bytes = None
        self.nfft_peak = 1024*16
        self.peak_signal = np.zeros((self.nfft_peak*2))
        self.peak_signal_index = 0
        self.wpm = 17
        self.nfft = 256
        self.noverlap = 183
        self.nperseg = 256
        self.thr = 1e-9
        self.pred_len = 0
        self.predictions = predictions.Predictions()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.predictions.load_model(os.path.join(self.script_dir, "models", "default.model"))
        self.dataq = queue.Queue()
        self.predworker = predworker.PredictionsWorker(self.predictions, self.dataq)
        self.predthread = QThread(self)
        self.initUI()
        self.startPredWorker()

    def startPredWorker(self):
        self.predworker.moveToThread(self.predthread)
        self.predthread.started.connect(self.predworker.run)
        self.predworker.dataReady.connect(self.pred_data)
        self.predworker.newChar.connect(self.new_char)
        self.predthread.start()

    def stopPredWorker(self):
        self.predworker.running = False
        self.predthread.quit()
        self.predthread.wait()
        print("stopPredWorker: done")

    def quitApplication(self):
        self.stopPredWorker()
        print("About to quit")
        QtWidgets.qApp.quit()

    def pred_data(self):
        self.sc_pred.new_data(self.predictions.cbuffer, self.predictions.p_preds_t)
        self.sc_hist.new_data(self.predworker.decoder.his)

    def new_char(self, char):
        cursor = QTextCursor(self.textbox.document())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(char)

    def initUI(self):
        plt.style.use('dark_background')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.script_dir, 'doc', 'img', 'MorseAngel_icon.png')))
        exitAct = QtWidgets.QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.quitApplication)

        audioAct = QtWidgets.QAction('&Device', self)
        audioAct.triggered.connect(self.openAudioDialog)

        self.statusLabel = QtWidgets.QLabel(self)
        self.fftLabel = QtWidgets.QLabel(self)
        self.nnLabel = QtWidgets.QLabel(self)
        self.nnLabel.setText(f"NN {self.predictions.device}")
        self.statusBar().addWidget(self.statusLabel)
        self.statusBar().addWidget(self.fftLabel)
        self.statusBar().addWidget(self.nnLabel)
        self.statusLabel.setText('Ready')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        audioMenu = menubar.addMenu('&Audio')
        audioMenu.addAction(audioAct)

        vbox = QtWidgets.QVBoxLayout()
        # line 1
        hbo1 = QtWidgets.QHBoxLayout()
        self.sc_time = MplTimeCanvas(self, width=5, height=2, dpi=100)
        self.sc_peak = MplPeakCanvas(self, width=4.5, height=2, dpi=100)
        self.controls = controls.ControlWidget()
        self.controls.wpmSignal.connect(self.wpmChange)
        self.controls.thrSignal.connect(self.thrChange)
        hbo1.addWidget(self.sc_time, 1)
        hbo1.addWidget(self.sc_peak, 1)
        hbo1.addWidget(self.controls, 1)
        hbo1_widget = QtWidgets.QWidget()
        hbo1_widget.setLayout(hbo1)
        # line 2
        hbo2 = QtWidgets.QHBoxLayout()
        self.sc_tenv = MplTimeCanvas(self, width=5, height=2, dpi=100)
        self.sc_zenv = MplTimeCanvas(self, width=5, height=2, dpi=100)
        hbo2.addWidget(self.sc_tenv, 2)
        hbo2.addWidget(self.sc_zenv, 1)
        hbo2_widget = QtWidgets.QWidget()
        hbo2_widget.setLayout(hbo2)
        # line 3
        hbo3 = QtWidgets.QHBoxLayout()
        self.textbox = QtWidgets.QTextEdit(self)
        self.sc_hist = MplHistCanvas(self, width=5, height=2, dpi=100)
        hbo3.addWidget(self.textbox, 2)
        hbo3.addWidget(self.sc_hist, 1)
        hbo3_widget = QtWidgets.QWidget()
        hbo3_widget.setLayout(hbo3)
        # line 4
        hbo4 = QtWidgets.QHBoxLayout()
        self.sc_pred = MplPredCanvas(self, width=5, height=2.5, dpi=100)
        hbo4.addWidget(self.sc_pred)
        hbo4_widget = QtWidgets.QWidget()
        hbo4_widget.setLayout(hbo4)
        # vbox
        vbox.addWidget(hbo1_widget)
        vbox.addWidget(hbo2_widget)
        vbox.addWidget(hbo3_widget)
        vbox.addWidget(hbo4_widget)
        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setGeometry(100, 100, 1400, 800)
        self.setWindowTitle('MorseAngel')
        self.show()

        self.initTEnv()
        self.initZEnv()

    def initTEnv(self):
        tenv_size = (self.audio_rate//(self.nfft-self.noverlap)) * 4
        self.sc_tenv.set_mp(tenv_size)
        #print(f"Init tenv {tenv_size}")

    def initZEnv(self):
        zenv_size = 50
        self.sc_zenv.set_mp(zenv_size)
        print(f"Init zenv {zenv_size}")

    def openAudioDialog(self, audio_devices): # Opening a new popup window...
        self.audio_dialog = audiodialog.AudioDialog()
        self.audio_dialog.set_audio_devices(self.audio_devices)
        self.a = self.audio_dialog.exec_() #exec_() for python2.x, before python3
        if self.a == self.audio_dialog.Accepted:
            self.audio_device = self.audio_devices[self.audio_dialog.device_index]
            self.audio_rates = self.audio_device.supportedSampleRates()
            self.audio_rate = self.audio_rates[self.audio_dialog.device_rate_index]
            self.statusLabel.setText(f'{self.audio_device.deviceName()} {self.audio_rate} S/s')
            print(self.audio_device.deviceName(), self.audio_rate)
            self.set_audio_device()
        elif self.a == self.audio_dialog.Rejected: #0
            print("Rejected")

    def wpmChange(self, wpm):
        self.wpm = wpm
        self.nfft, self.noverlap = fft_optim(Fs=self.audio_rate, code_speed=self.wpm)
        self.fftLabel.setText(f'FFT {self.nfft} OVL {self.noverlap}')
        self.set_audio_device()

    def thrChange(self, thr):
        self.thr = thr*0.9

    def set_audio_device(self):
        format = QtMultimedia.QAudioFormat()
        format.setSampleRate(self.audio_rate)
        format.setChannelCount(1)
        format.setByteOrder(QtMultimedia.QAudioFormat.LittleEndian)
        format.setSampleType(QtMultimedia.QAudioFormat.Float)
        if (self.audio_device.isFormatSupported(format) is not True):
            format = self.audio_device.nearestFormat(format)
        self.audio_rate = format.sampleRate()
        self.audio_bytes = format.bytesPerFrame()
        if self.audio_input:
            self.audio_input.stop()
        else:
            print("Init Audio")
        self.audio_input = QtMultimedia.QAudioInput(self.audio_device, format)
        self.audio_nsamples = self.audio_rate//2
        self.nfft, self.noverlap = fft_optim(Fs=self.audio_rate, code_speed=self.wpm)
        self.fftLabel.setText(f'FFT {self.nfft} OVL {self.noverlap}')
        #print(f"FFT {self.nfft} with overlap {self.noverlap}")
        self.sc_time.set_mp(self.audio_nsamples)
        self.sc_peak.set_mp()
        self.audio_input.setBufferSize(self.audio_nsamples)
        self.initTEnv()
        self.audio_buffer = self.audio_input.start()
        self.audio_buffer.readyRead.connect(self.audioRead)
        self.predworker.reset_hist()

    def audioRead(self):
        buffer_bytes = self.audio_buffer.readAll()
        if buffer_bytes:
            buffer_bytes = buffer_bytes[:self.audio_nsamples*self.audio_bytes] # truncate
            data = np.frombuffer(buffer_bytes, dtype=np.single)
            if max(data) > 0:
                #print(type(data), data.shape)
                data /= max(max(data), -min(data))
                # data /= (max(data)/2.0)
                # data[data > 1] = 1
                # data[data < -1] = -1
                self.sc_time.new_data(data)
                nb_samples = len(buffer_bytes) // self.audio_bytes
                self.peak_signal[self.peak_signal_index:self.peak_signal_index+nb_samples] = data
                self.peak_signal_index += nb_samples
                if self.peak_signal_index > self.nfft_peak:
                    f, s = periodogram(self.peak_signal, self.audio_rate, 'blackman', self.nfft_peak, 'linear', False, scaling='spectrum')
                    threshold = max(s)*0.9
                    if threshold > self.thr:
                        maxtab, mintab = peakdet(abs(s[0:int(len(s)/2-1)]), threshold, f[0:int(len(f)/2-1)])
                        tone = maxtab[0,0]
                        #print(f'tone: {tone} thr: {(10.0 * np.log10(threshold)):.2f} dB')
                        self.sc_peak.new_data(f, s, maxtab, tone)
                        nside_bins = 1
                        f, t, img = specimg(self.audio_rate, self.peak_signal[:self.nfft_peak], tone, self.nfft, self.noverlap, nside_bins)
                        #print(t.shape, f)
                        if len(f) != 0:
                            img_line = np.sum(img, axis=0)
                            img_line /= (max(img_line)/1.5)
                            img_line[img_line > 1] = 1
                            if len(img_line) != self.pred_len:
                                self.pred_len = len(img_line)
                                self.sc_pred.set_mp(self.pred_len*3)
                            self.dataq.put(img_line)
                            #self.test_line(img_line, 0.75)
                            self.sc_tenv.new_data(img_line, 50)
                            self.sc_zenv.new_data(img_line[:50])
                    self.peak_signal = np.roll(self.peak_signal, self.nfft_peak, axis=0)
                    self.peak_signal_index -= self.nfft_peak

    @staticmethod
    def test_line(img_line, thr):
        count = 0
        hist = {}
        for x in img_line:
            if x > thr:
                count += 1
            elif count != 0:
                hist[count] = hist.setdefault(count, 0) + 1
                count = 0
        print(dict(sorted(hist.items(), key=lambda item: item[1], reverse=True)))


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(make_palette())
    w = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
