import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import periodogram, spectrogram
import audiodialog, controls
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
           self.axes.lines.pop(0)
        self.time_line, = self.axes.plot(self.time_vect, np.ones_like(self.time_vect)/2, color="blue")
        self.draw()

    def new_data(self, data, zoom_span=0):
        plotdata = self.time_line.get_data()[1]
        nb_samples = len(data)
        plotdata = np.roll(plotdata, -nb_samples, axis=0)
        plotdata[-nb_samples:] = data
        ymin = min(data)
        ymax = max(data)
        self.axes.set_ylim(ymin, ymax)
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


class MplPeakCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(which='both')
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
            self.spec_line, = self.axes.plot(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]),'g-')
        else:
            self.spec_line.set_data(f[0:int(len(f)/2-1)], abs(s[0:int(len(s)/2-1)]))
        pmax = max(s)
        self.axes.set_ylim(1e-5, pmax)
        self.axes.set_xlabel(f'F (Hz) - {tone:9.5f} ({10*np.log10(pmax):5.2f} dB)')
        #self.fig.suptitle(f"Signal peak {10*np.log10(pmax):5.2f} dB found at {tone:9.5f} Hz")
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
        self.initUI()

    def initUI(self):
        exitAct = QtWidgets.QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(QtWidgets.qApp.quit)

        audioAct = QtWidgets.QAction('&Device', self)
        audioAct.triggered.connect(self.openAudioDialog)

        self.statusLabel = QtWidgets.QLabel(self)
        self.fftLabel = QtWidgets.QLabel(self)
        self.statusBar().addWidget(self.statusLabel)
        self.statusBar().addWidget(self.fftLabel)
        self.statusLabel.setText('Ready')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        audioMenu = menubar.addMenu('&Audio')
        audioMenu.addAction(audioAct)

        vbox = QtWidgets.QVBoxLayout()
        hbo1 = QtWidgets.QHBoxLayout()
        self.sc_time = MplTimeCanvas(self, width=5, height=3, dpi=100)
        self.sc_peak = MplPeakCanvas(self, width=5, height=3, dpi=100)
        self.controls = controls.ControlWidget()
        self.controls.wpmSignal.connect(self.wpmChange)
        self.controls.thrSignal.connect(self.thrChange)
        hbo1.addWidget(self.sc_time, 1)
        hbo1.addWidget(self.sc_peak, 1)
        hbo1.addWidget(self.controls, 1)
        hbo2 = QtWidgets.QHBoxLayout()
        self.sc_tenv = MplTimeCanvas(self, width=5, height=3, dpi=100)
        self.sc_zenv = MplTimeCanvas(self, width=5, height=3, dpi=100)
        hbo2.addWidget(self.sc_tenv, 2)
        hbo2.addWidget(self.sc_zenv, 1)
        hbo1_widget = QtWidgets.QWidget()
        hbo1_widget.setLayout(hbo1)
        hbo2_widget = QtWidgets.QWidget()
        hbo2_widget.setLayout(hbo2)
        vbox.addWidget(hbo1_widget)
        vbox.addWidget(hbo2_widget)
        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setGeometry(100, 100, 1400, 600)
        self.setWindowTitle('MorseAngel')
        self.show()

        self.initTEnv()
        self.initZEnv()

    def initTEnv(self):
        tenv_size = (self.audio_rate//(self.nfft-self.noverlap)) * 4
        self.sc_tenv.set_mp(tenv_size)
        print(f"Init tenv {tenv_size}")

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
        print(f"FFT {self.nfft} with overlap {self.noverlap}")
        self.set_audio_device()

    def thrChange(self, thr):
        self.thr = thr
        print(f"Threshold {self.thr}")

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
        print(f"FFT {self.nfft} with overlap {self.noverlap}")
        self.sc_time.set_mp(self.audio_nsamples)
        self.sc_peak.set_mp()
        self.audio_input.setBufferSize(self.audio_nsamples)
        self.initTEnv()
        self.audio_buffer = self.audio_input.start()
        self.audio_buffer.readyRead.connect(self.audioRead)

    def audioRead(self):
        buffer_bytes = self.audio_buffer.readAll()
        if buffer_bytes:
            buffer_bytes = buffer_bytes[:self.audio_nsamples*self.audio_bytes] # truncate
            data = np.frombuffer(buffer_bytes, dtype=np.single)
            if max(data) > 0:
                #print(max(data))
                data /= max(data)
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
                        print(t.shape, f)
                        if len(f) != 0:
                            img_line = np.sum(img, axis=0)
                            img_line /= max(img_line)
                            self.test_line(img_line, 0.75)
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
    w = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
