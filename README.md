# Yolo4Apnea
Real-time detection of obstructive sleep apna

# Usage
**Usage:** yolo4apnea.py [-h] [-p] [-x] FILENAME

Predict Apnea events on .edf file

## Positional arguments:

  **FILENAME**    path to a .edf file to analyze


## Optional arguments:
  **-h, --help**  show this help message and exit
  
  **-p**          Output png predictions to out/
  
  **-x, -xml**    Output predictions annotations to xml file


# Installation
## Linux
1. Clone this repository
```bash
git clone https://github.com/simula-vias/Yolo4Apnea.git
cd Yolo4Apnea
```
2. Install darknet from https://github.com/AlexeyAB/darknet

### As of Feb 25 2020 you can run these commands 
```bash
git clone https://github.com/AlexeyAB/darknet.git
cd darknet

mkdir build-release
cd build-release
cmake ..
make
make install
```

## Windows / OSX
currently not supported
