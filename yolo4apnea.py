import os
import pyedflib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import re
import argparse

from PIL import Image


XLIM = 90 * 10
OVERLAP = 45 * 10

def readEdfFile(file):
    print(os.getcwd())
    print(f"reading file {file}")
    try:
        edf  = pyedflib.EdfReader(file)
        cols = edf.getSignalLabels()
    
        thor_res = pd.Series(edf.readSignal(cols.index("THOR RES")),name="THOR_RES")
        abdo_res = pd.Series(edf.readSignal(cols.index("ABDO RES")),name="ABDO_RES")
        signals = thor_res.to_frame().join(abdo_res)

    finally:
        edf._close()
        del edf

    return signals

def generate_image_from_signal(signal):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(signal.index, signal["ABDO_RES"])
    ax.set_ylim(-1, 1)
    ax.grid(False)
    fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    for i in range(0,len(signal),OVERLAP):
        ax.set_xlim(i,i + XLIM)
        fig.savefig(f"tmp/{i}.png")

def plot_events(signal,events):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(signal.index, signal["ABDO_RES"])
    ax.set_ylim(-1, 1)
    ax.grid(False)
    fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    for line in events.itertuples():
        ax.set_xlim(line.PRED_START-100,line.PRED_END +100)
        print(line.CONFIDENCE)
        test = ax.axvspan(line.PRED_START, line.PRED_END, alpha=line.CONFIDENCE/100, color='red')
        fig.savefig(f"../out/{line.PRED_START}.png")
        test.remove()




def get_predictions():
    predictions = pd.DataFrame(columns=['IMG_START', 'PRED_START', 'PRED_END','CONFIDENCE'])
    image_width = Image.open("../tmp/0.png").size[0]
    pixel_duration = image_width/XLIM

    print(pixel_duration)
    with open("predictions.txt","r") as f:
        for line in f:
            line = line[0:-1]
            new_image = re.search(r"tmp\/(\d+).png:",line)
            if new_image:
                start_value = int(new_image.group(1))
            new_apnea = re.search(r"apnea:\D(\d+)%.*left_x:\D*(\d+).*width:\D*(\d+)",line)
            if new_apnea:
                confidence = int(new_apnea.group(1))
                apnea_start = start_value + (int(new_apnea.group(2))/ pixel_duration)
                apnea_width = apnea_start + (int(new_apnea.group(3))/ pixel_duration)
                predictions = predictions.append({'IMG_START':start_value, "PRED_START":apnea_start,"PRED_END" : apnea_width,"CONFIDENCE" :confidence }, ignore_index=True)
    return predictions



def predict_edf(file):
    signal = readEdfFile(file)
    #generate_image_from_signal(signal)
    files = ""
    curdir = os.getcwd()

    for image in glob.iglob(f"tmp{os.sep}*"):
        files += f"{curdir}{os.sep}{image}\n"


    os.chdir("darknet")
    with open("generate.txt","w") as f:
        f.write(files)
    

    #os.system(("./darknet detector test ../obj.data yolo-obj.cfg yolo-obj_10000.weights -ext_output < generate.txt > predictions.txt"))

    predictions = get_predictions()

    threshold = 30
    predictions = predictions[predictions.CONFIDENCE > threshold]
    apnea_prediction = np.zeros(int(predictions.PRED_END.max()))


    for line in predictions.itertuples():
        for index in range(int(line.PRED_START), int(line.PRED_END)):
            if apnea_prediction[index] < line.CONFIDENCE:
                apnea_prediction[index] = line.CONFIDENCE

    print(apnea_prediction)
    plot_events(signal,predictions)
    #Delete the temporary files
    #for image in glob.iglob(f"tmp{os.sep}*"):
    #    os.remove(f"{curdir}{os.sep}{image}")

    #os.remove("generate.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict Apnea events on .edf file ')
    parser.add_argument('file',metavar="FILENAME", help='path to a .edf file to analyze')
    parser.add_argument('-p', help='Output png predictions to out/', action="store_true")
    parser.add_argument("-x",'-xml', help='Output png predictions to out/', action="store_true")


    args = parser.parse_args()
    
    #test_file = "shhs1-200001.edf"
    #predict_edf(test_file)

    #os.system(("./darknet detect cfg/yolov3.cfg yolov3.weights data/dog.jpg"))
