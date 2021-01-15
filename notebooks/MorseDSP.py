from scipy.signal import periodogram, spectrogram
from peakdetect import peakdet

def find_peak(Fs, signal):
    """ Find the signal frequency and maximum value
    """
    f,s = periodogram(signal, Fs, 'blackman', 1024*32, 'linear', False, scaling='spectrum')
    threshold = max(s)*0.9  # only 0.4 ... 1.0 of max value freq peaks included
    maxtab, mintab = peakdet(abs(s[0:int(len(s)/2-1)]), threshold, f[0:int(len(f)/2-1)])
    return maxtab, f, s

def specimg(Fs, signal_orig, tbegin, tend, tone, nfft, wbins, complex=False):
    """ Create spectral image around tone frequency
    """
    signal = signal_orig[tbegin*Fs if tbegin else None: tend*Fs if tend else None]
    noverlap = 224 if nfft//2 >= 256 else nfft//2
    f, t, Sxx = spectrogram(signal, Fs, nfft=nfft, noverlap=noverlap, scaling='density')
    fbin = (tone/(Fs/2))* (len(f)-1)
    if complex:
        fbin /= 2
    center_bin = int(round(fbin))
    return f[center_bin-wbins:center_bin+wbins+1], t, Sxx[center_bin-wbins:center_bin+wbins+1,:], noverlap

def specimgphi(Fs, signal_orig, tbegin, tend, tone, nfft, wbins):
    """ Create phase spectral image around tone frequency
    """
    signal = signal_orig[tbegin*Fs if tbegin else None: tend*Fs if tend else None]
    noverlap = 224 if nfft//2 >= 256 else nfft//2
    f, t, Sxx = spectrogram(signal, Fs, nfft=nfft, noverlap=noverlap, mode='angle')
    fbin = (tone/(Fs/2))* (len(f)-1)
    fbin /= 2
    center_bin = int(round(fbin))
    return f[center_bin-wbins:center_bin+wbins+1], t, Sxx[center_bin-wbins:center_bin+wbins+1,:], noverlap

def specline(Fs, signal_orig, tbegin, tend, tone, nfft):
    """ Create spectral line centered on tone frequency
    """
    signal = signal_orig[tbegin*Fs if tbegin else None: tend*Fs if tend else None]
    noverlap = 224 if nfft//2 >= 256 else nfft//2
    f, t, Sxx = spectrogram(signal, Fs, nfft=nfft, noverlap=noverlap, scaling='density')
    fbin = (tone/(Fs/2))* (len(f)-1)
    center_bin = int(round(fbin))
    return f[center_bin], t, Sxx[center_bin,:], noverlap