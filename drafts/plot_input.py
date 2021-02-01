#!/usr/bin/env python3
"""Plot signal(s) on stdin with matplotlib.

Matplotlib and NumPy have to be installed.
Hardcoded for 1 channel single precision float

Ex with pulseaudio:
parec -d alsa_output.pci-0000_00_1f.3.analog-stereo.monitor --channels=1 --format=float32le --raw  | ./plot_input.py

"""
import argparse
import queue
import sys
import threading

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'channels', type=int, default=[1], nargs='*', metavar='CHANNEL',
    help='input channels to plot (default: the first)')
parser.add_argument(
    '-w', '--window', type=float, default=200, metavar='DURATION',
    help='visible time slot (default: %(default)s ms)')
parser.add_argument(
    '-i', '--interval', type=float, default=30,
    help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument(
    '-b', '--blocksize', type=int, default=4096, help='block size (in samples)')
parser.add_argument(
    '-r', '--samplerate', type=float, default=48000.0, help='sampling rate of audio device')
parser.add_argument(
    '-n', '--downsample', type=int, default=10, metavar='N',
    help='display every Nth sample (default: %(default)s)')
parser.add_argument(
    '-g', '--gain', type=float, default=1.0, help='linear gain: %(default)s)')
args = parser.parse_args(remaining)
if any(c < 1 for c in args.channels):
    parser.error('argument CHANNEL: must be >= 1')
mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
q = queue.Queue()
run = True


def read_input(length):
    while run:
        buff = sys.stdin.buffer.read(length)
        q.put(buff)

def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)//4
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = args.gain*np.frombuffer(data, dtype=np.single).reshape(shift,1)
    for column, line in enumerate(lines):
        line.set_ydata(plotdata[:, column])
    return lines


try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((length, len(args.channels)))

    fig, ax = plt.subplots()
    lines = ax.plot(plotdata)
    if len(args.channels) > 1:
        ax.legend(['channel {}'.format(c) for c in args.channels],
                  loc='lower left', ncol=len(args.channels))
    ax.axis((0, len(plotdata), -1, 1))
    ax.yaxis.grid(True)
    ax.xaxis.grid(True)
    ax.tick_params(bottom=True, top=False, labelbottom=True,
                   right=False, left=True, labelleft=True)
    fig.tight_layout(pad=0)

    x = threading.Thread(target=read_input, args=[length*4])
    x.start()

    ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True)
    plt.show()
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
finally:
    run = False
