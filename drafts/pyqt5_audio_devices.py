import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import periodogram, spectrogram
import audiodialog
sys.path.append('../notebooks')
from peakdetect import peakdet

def get_audioin_devices():
    return QtMultimedia.QAudioDeviceInfo.availableDevices(QtMultimedia.QAudio.AudioInput)

def print_devices(devices):
    for device in devices:
        print(device.deviceName(), device.supportedSampleRates())

def specimg(Fs, signal, tone, nfft, noverlap, wbins, complex=False):
    """ Create spectral image around tone frequency
    """
    nperseg = nfft if nfft < 256 else 256
    f, t, Sxx = spectrogram(signal, Fs, nfft=nfft, noverlap=noverlap, nperseg=nperseg, scaling='density')
    fbin = (tone/(Fs/2))* (len(f)-1)
    if complex:
        fbin /= 2
    center_bin = int(round(fbin))
    return f[center_bin-wbins:center_bin+wbins+1], t, Sxx[center_bin-wbins:center_bin+wbins+1,:]

class TestFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, parent)


class MplTimeCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both')
        self.axes.set_xlabel(u'samples')
        self.fig.tight_layout(pad=0)
        self.time_line = None
        super(MplTimeCanvas, self).__init__(self.fig)

    def set_mp(self, nsamples):
        self.time_vect = np.arange(nsamples)
        self.axes.set_ylim(-1, 1)
        self.axes.set_xlim(0, nsamples)
        if self.time_line:
           self.axes.lines.pop(0)
        self.time_line, = self.axes.plot(self.time_vect, np.ones_like(self.time_vect)/2, color="blue")
        self.draw()

    def new_data(self, data):
        plotdata = self.time_line.get_data()[1]
        nb_samples = len(data)
        plotdata = np.roll(plotdata, -nb_samples, axis=0)
        plotdata[-nb_samples:] = data
        self.axes.set_ylim(min(data), max(data))
        self.time_line.set_data(self.time_vect, plotdata)
        self.draw()


class MplPeakCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both')
        self.axes.set_xlabel(u'Frequency (Hz)')
        self.axes.set_ylabel(u'Amplitude (log)')
        self.axes.set_yscale('log')
        self.spec_line = None
        super(MplPeakCanvas, self).__init__(self.fig)

    def set_mp(self):
        if self.spec_line:
            self.axes.lines.pop(0)
        self.spec_line = None

    def new_data(self, f, s, maxtab, tone):
        if not self.spec_line:
            self.spec_line, = self.axes.plot(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]),'g-')
        else:
            self.spec_line.set_data(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]))
        pmax = max(s)
        self.axes.set_ylim(1e-11, pmax)
        self.fig.suptitle(f"Signal peak {10*np.log10(pmax):5.2f} dB found at {tone:9.5f} Hz")
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
        self.peak_signal = np.zeros((1024*32*2))
        self.peak_signal_index = 0
        self.nfft = 128 # 256,220
        self.noverlap = 56
        self.initUI()

    def initUI(self):
        exitAct = QtWidgets.QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.qApp.quit)

        audioAct = QtWidgets.QAction('&Device', self)
        audioAct.setStatusTip('Select device')
        audioAct.triggered.connect(self.openAudioDialog)

        self.statusBar().showMessage('Ready')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        audioMenu = menubar.addMenu('&Audio')
        audioMenu.addAction(audioAct)

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        self.sc_time = MplTimeCanvas(self, width=5, height=3, dpi=100)
        self.sc_peak = MplPeakCanvas(self, width=5, height=3, dpi=100)
        self.sc_tenv = MplTimeCanvas(self, width=5, height=3, dpi=100)
        hbox.addWidget(self.sc_time)
        hbox.addWidget(self.sc_peak)
        top_widget = QtWidgets.QWidget()
        top_widget.setLayout(hbox)
        vbox.addWidget(top_widget)
        vbox.addWidget(self.sc_tenv)
        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setGeometry(100, 100, 800, 300)
        self.setWindowTitle('MorseAngel')
        self.show()

        self.initTEnv()

    def initTEnv(self):
        tenv_size = (1024*32//(self.nfft-self.noverlap)) * 1
        self.sc_tenv.set_mp(tenv_size)
        print(f"Init tenv {tenv_size}")

    def openAudioDialog(self, audio_devices): # Opening a new popup window...
        self.audio_dialog = audiodialog.AudioDialog()
        self.audio_dialog.set_audio_devices(self.audio_devices)
        self.a = self.audio_dialog.exec_() #exec_() for python2.x, before python3
        if self.a == self.audio_dialog.Accepted:
            self.audio_device = self.audio_devices[self.audio_dialog.device_index]
            self.audio_rates = self.audio_device.supportedSampleRates()
            self.audio_rate = self.audio_rates[self.audio_dialog.device_rate_index]
            print(self.audio_device.deviceName(), self.audio_rate)
            self.set_audio_device()
        elif self.a == self.audio_dialog.Rejected: #0
            print("Rejected")

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
        self.sc_time.set_mp(self.audio_nsamples)
        self.sc_peak.set_mp()
        self.audio_input.setBufferSize(self.audio_nsamples)
        self.audio_buffer = self.audio_input.start()
        self.audio_buffer.readyRead.connect(self.audioRead)

    def audioRead(self):
        buffer_bytes = self.audio_buffer.readAll()
        if buffer_bytes:
            buffer_bytes = buffer_bytes[:self.audio_nsamples*self.audio_bytes] # truncate
            data = np.frombuffer(buffer_bytes, dtype=np.single)
            if max(data) > 0:
                self.sc_time.new_data(data)
                nb_samples = len(buffer_bytes) // self.audio_bytes
                self.peak_signal[self.peak_signal_index:self.peak_signal_index+nb_samples] = data
                self.peak_signal_index += nb_samples
                if self.peak_signal_index > 1024*32:
                    f, s = periodogram(self.peak_signal, self.audio_rate, 'blackman', 1024*32, 'linear', False, scaling='spectrum')
                    threshold = max(s)*0.9
                    if threshold > 2e-9:
                        maxtab, mintab = peakdet(abs(s[0:int(len(s)/2-1)]), threshold, f[0:int(len(f)/2-1)])
                        tone = maxtab[0,0]
                        #print(f'tone: {tone} thr: {(10.0 * np.log10(threshold)):.2f} dB')
                        self.sc_peak.new_data(f, s, maxtab, tone)
                        nside_bins = 1
                        f, t, img = specimg(self.audio_rate, self.peak_signal[:1024*32], tone, self.nfft, self.noverlap, nside_bins)
                        print(t.shape, f)
                        img_line = np.sum(img, axis=0)
                        img_line /= max(img_line)
                        self.sc_tenv.new_data(img_line)
                    self.peak_signal = np.roll(self.peak_signal, 1024*32, axis=0)
                    self.peak_signal_index -= 1024*32


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
