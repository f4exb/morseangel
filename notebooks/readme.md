# Experimental notebooks

This section features some Jupyter notebooks that have been used to exercise and demonstrate deep learning experiments aiming at decoding Morse code from an audio signal or the preprocessed envelope waveform.

## Running environment

These notebooks can be run inside the [GPU-Jupyter](https://github.com/iot-salzburg/gpu-jupyter) Docker image that features a GPU enabled (if you use a NVIDIA graphics card) complete environment to run Data Science or Deep Learning notebooks using [Tensorflow](https://www.tensorflow.org/) with [Keras](https://keras.io/) or [PyTorch](https://pytorch.org/).

The GPU-Jupyter Docker image can be built from the repository mentioned above or ready made Docker images can be found in [Docker Hub](https://hub.docker.com/r/cschranz/gpu-jupyter)

## The notebooks

### Morse keying

This series of notebooks present models that try to discover the distinctive features of the Morse code keying that is:

  - The envelope
  - The "dit"
  - The "dah"
  - The element separator at the end of a "dit" or a "dah"
  - The character separator
  - The word separator

#### RNN-Morse-keras

This notebook is based on Mauri AG1LE's work back in 2015 that can be found on Github [here](https://github.com/ag1le/RNN-Morse). From an audio signal generated at 8 kHz sample rate (thus in 4 kHz bandwidth) it attempts to recognize Morse code distinctive features described above.

It trains a LSTM based recurrent neural network (RNN) on a slightly noisy signal (a few dB SNR in 4 kHz bandwidth) in an encoder-decoder fashion. The envelope of the signal is taken as input as a time series of floating point values and the labels are also time series of the 6 signals described above.

It then attempts prediction on a much noisier signal of the same test data to see how it can perform in retrieving the 6 predicted signals and reformat the original envelope.

This implementation is based on Keras / Tensorflow as in the original noebooks from Mauri.

#### RNN-Morse-pytorch

This is the same as `RNN-Morse-keras` but transposed in the PyTorch framework.

#### RNN-Morse-envelope

Starting from `RNN-Morse-pytorch` it will skip the audio processing to work directly on the envelope that would be the result of the audio processing. This is to simplify the processing in view of producing a much larger quantity of data that will be necessary to train models for Morse code recognition. As a first step it is necessary to verify that the data produced this way works with the simpler Morse keying recognition models.

#### RNN-Morse-filter

Starting from `RNN-Morse-envelope` the model focuses on envelope denoising. It is based on the encoder-decoder concept taking 5 hidden nodes which correspond to the number of distinctive Morse keying features described initially. It has been found that the model is more efficient if trained on very noisy signals at the expense of using more epochs. In fact it should be trained with the noisiest signals expected.

#### RNN-Morse-filter2

Starting from `RNN-Morse-filter` a pure noise channel is added along the noisy signal channel in an attempt for the network to better identify silence periods. This is not any better if not worse.

#### RNN-Morse-features

Also from `RNN-Morse-envelope` the model tries to find the keying features explicitly. Then dits, dahs and possibly silences are tried in different combinations to reconstruct the signal in the same attempt of denoising the original signal.

#### RNN-Morse-full

From `RNN-Morse-features` adds the envelope signal in the training. It is not any better than `RNN-Morse-features` or `RNN-Morse-filter` anyway hard to tell the difference.

### Morse decoding

Building on previous experience we now try to decode complete characters

#### RNN-Morse-chars_feat

Here we just add character labels to feature labels. The whole character is labeled. Does not provide good results

#### RNN-Morse-chars

Here we just have the character labels.  The whole character is labeled.  This proves to be even worse

#### RNN-Morse-chars-2step

This is a combination of a first LSTM and Linear layers to find a limited set of features that is the same number of features as in the keying recognition in the hope that it will learn the keying features by itself. Thus these are "hidden" features. Then the result is used in a second LSTM and Linear layers combination that provides the final character features output. This does not work at all.

The whole character is labeled.

#### Morse decoding logic from keying recognition

In `RNN-Morse-chars-hyb` we attempt to decode morse code in procedural logic from the keying recognition data post-processed from keying model. This sort of works if the signal is not too noisy. and is a good first step towards next tests by introducing decoding along the "Morse tree".

#### RNN-Morse-chars-dual

This is a dual model approach where a first model is trained on the keying features thus analogous to RNN-Morse-features and the predictions are then used in a second model trained on character labels.

The important point at this stage is that the labeling has changed. Basically it follows the trip along the "Morse tree" that has been seen previously in the procedural decoding. The important point is to get the character space feature correctly to be able to return to the start state. Fortunately this gets fairly well spotted by the keying model.

It proves to be significantly better that all previous character decoding tests. By gating the character lines with the character separator line (just a multiplication) one can find the right character as the one with the line having the maximum value. Spaces are simply given by the word separator line.

### Drafts

  - `dataset.ipynb`: playing with Pandas datasets
  - `gpu.ipynb`: GPU detection
  - `morse.ipynb`: playing with Morse generator
  - `noise.ipynb`: tuning noise generation
  - `tensors.ipynb`: playing with tensors
  - `time_series.ipynb`: time series specific issues
  - `tqdn.ipynb`: playing with tqdm progress bar