![MorseAngel banner](doc/img/morseangel_banner.png)

# Deep Neural Networks for Morse decoding

## Contents

### notebooks

This folder contains development Jupyter notebooks. It contains all notebooks from early stage to more elaborated models. The models are trained in the notebooks.

Please check the `readme.md` file in the `notebooks` folder for more information.

### drafts

Some pure python drafts

### main folder

This is the main application folder containing `morseangel.py` and its dependencies

## Start

You will need Python3 and virtualenv installed in your system. Firstly create and activate a virtual environment:

```sh
virtualenv venv
. ./venv/bin/activate
```

Install prerequisites with pip:

```sh
pip install -r requirements.txt
```

Start application:

```sh
python ./morseangel.py
```
