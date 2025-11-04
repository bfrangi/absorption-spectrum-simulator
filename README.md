# Absorption Spectrum Simulator

Useful script for simulating absorption spectra.

## Setup

Before starting, if you are going to be using the HITRAN/HITEMP databases, create a Hitran
login [here](https://hitran.org/login/). Other databases may require their own credentials.

### Linux

1. Clone the repository:

```bash
git clone https://github.com/bfrangi/absorption-spectrum-simulator.git
cd absorption-spectrum-simulator
```

2. Install `virtualenv` and create a virtual environment:

```bash
sudo apt-get update
sudo apt-get install python3-venv
python3.10 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. [Optional] If you want to use LaTeX for plotting, install the `texlive` package:

```bash
sudo apt-get update
sudo apt-get install texlive-latex-extra texlive-fonts-extra dvipng
```

### Windows

1. Clone the repository:

```bash
git clone https://github.com/bfrangi/absorption-spectrum-simulator.git
cd absorption-spectrum-simulator
```

2. Install `python3.12` from the Microsoft Store.

3. Create a virtual environment:

```bash
python3.12 -m venv .venv
.\.venv\Scripts\activate.bat
```

4. Install dependencies:

```bash
pip install -r requirements-win.txt
```

5. [Optional] If you want to use LaTeX for plotting, install the `texlive` package by downloading
   the installer from [here](https://www.tug.org/texlive/windows.html) or the ISO from 
   [here](https://www.tug.org/texlive/acquire-iso.html) and following the installation
   instructions.

## Usage

If using HITRAN/HITEMP, you will need to log in with your HITRAN credentials the first time you
simulate an absorption spectrum. Other databases may require their own credentials.

**Note**: The first time you run the simulator, the database will be downloaded, and this could
take some time. Please be patient!

### Linux

1. Inside the activated python environment run the simulator with:

```bash
python src/simulator.py
```

### Windows

1. Inside the activated python environment run the simulator with:

```bash
python src\simulator.py
```

## Using GPU Acceleration

Check out the `GPU_DEVICE_ID` setting in `src/lib/defaults.py`. By default, it is set to `"nvidia"`
which will use the NVIDIA GPU if available. If you want to use a different GPU, run the
`src/identify-gpu.py` script to list available GPUs and set the `GPU_DEVICE_ID` accordingly (it can 
be the number of the GPU in the output list or a string contained in the name of the device).
