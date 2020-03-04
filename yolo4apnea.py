import os
import pyedflib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import glob
import re
import argparse
import progressbar
import shutil

from PIL import Image

XLIM = 90 * 10
OVERLAP = 45 * 10
out_folder = "out"
tmp_folder = "tmp"


"""
Checks whether Darknet is installed,
creates required folders if needed, 
and creates a obj.data that works for the current machine

Returns:
    None -- Only Side effects
"""
def setup():
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    if not os.path.isdir('darknet'):
        print("Please install darknet")
        exit(-1)

    if os.path.isdir(out_folder):
        shutil.rmtree(out_folder)

    os.makedirs(out_folder)

    if not os.path.isdir(tmp_folder):
        os.makedirs(tmp_folder)
        
    obj_data = f"classes= 1\nnames = {path}{os.sep}obj.names"

    with open("obj.data","w+") as f:
        f.write(obj_data)


"""
Reads EDF file from SHHS dataset. Will need adjustments to work for other signals

Returns:
    DataFrame -- Dataframe of thorax and abdominal signals, with index in deciseconds since start of recording
"""
def readEdfFile(file):
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

"""
Plots images from the signal dataframe in a predictable way. Starts a new image for every OVERLAP/10 seconds to map the whole recording

Returns:
    None -- outputs images in tmp/ folder
"""
def generate_image_from_signal(signal):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(signal.index, signal["ABDO_RES"])
    ax.set_ylim(-1, 1)
    ax.grid(False)
    fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    print("Creating images for analysis")
    j = 0
    with progressbar.ProgressBar(max_value=len(signal)) as prog:
        for i in range(0,len(signal),OVERLAP):
            ax.set_xlim(i,i + XLIM)
            prog.update(i)
            j+=1
            fig.savefig(f"tmp/{i}.png")
    print(f"DONE\nCreated {j} images")
"""
Plots the signal of the events that yolo predicted with signal before and after the event

Returns:
    None -- Outputs prediction images in /out folder
"""
def plot_events(signal,events):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(signal.index, signal["ABDO_RES"])
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Time (Deciseconds)")
    #ax.grid(False)
    #fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    with progressbar.ProgressBar(max_value=len(events)) as event:
        i = 0
        for line in events.itertuples():
            event.update(i)
            i +=1
            ax.set_xlim(line.PRED_START-400,line.PRED_END + 400)
            #marking = ax.axvspan(line.PRED_START, line.PRED_END, alpha=line.CONFIDENCE/100, color='red')
            ax.plot([line.PRED_START,line.PRED_END],[-0.6,-0.6],linewidth=3,color="r")
            ax.plot([line.PRED_START,line.PRED_START],[-0.5,-0.7],linewidth=3,color="r")
            ax.plot([line.PRED_END,line.PRED_END],[-0.5,-0.7],linewidth=3,color="r")
            ax.text(line.PRED_START-20, -0.75, line.PRED_START, family="serif")
            ax.text(line.PRED_END-20, -0.75, line.PRED_END, family="serif")

            extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
            leg = ax.legend([f"Prediction of apnea",f"Start = {line.PRED_START}",f"End = {line.PRED_END}",f"Confidence = {line.CONFIDENCE}"],loc="upper right")
            leg._legend_box.align = "right"

            fig.savefig(f"../out/{line.PRED_START}.png")
            #marking.remove()
    print("Done creating png files. See out/ for output")

"""
Analyses predictions.txt to convert yolos prediction to a dataframe for easier processing
converts pixelvalues from prediction to correct event-time since start of recording

Returns:
    Dataframe -- Dataframe with info about when the image starts,when the prediction starts, when the prediction ends, and confidence in prediction
"""
def get_predictions(demo):
    predictions = pd.DataFrame(columns=['IMG_START', 'PRED_START', 'PRED_END','CONFIDENCE'])
    image_width = Image.open("../tmp/0.png").size[0]
    pixel_duration = image_width/XLIM

    predictions_file = "./predictions.txt"

    if demo:
        predictions_file="../demo/predictions.txt"

    with open(predictions_file,"r") as f:
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


def clean_predictions(predictions):
    predictions = predictions.sort_values(by=["PRED_START"])
    ndf = []

    prev_to = -1
    prev_from = 0
    confidence = 200
    for index, row in predictions.iterrows():
        if prev_to == -1:
            prev_from = row["PRED_START"]
            prev_to = row["PRED_END"]
            confidence = row["CONFIDENCE"]
            
        elif row["PRED_START"] < prev_from and row["PRED_END"] > prev_to:
            prev_from = row["PRED_START"]
            prev_to = row["PREV_END"]
            confidence = confidence if row["CONFIDENCE"] > confidence else row["CONFIDENCE"]

        elif row["PRED_START"] > prev_from and row["PRED_END"] < prev_to:
            pass
        elif row["PRED_START"] < prev_to and row["PRED_END"] > prev_to :
            prev_to = row["PRED_END"]
            onfidence = confidence if row["CONFIDENCE"] > confidence else row["CONFIDENCE"]

        else:
            confidence = confidence if row["CONFIDENCE"] > confidence else row["CONFIDENCE"]
 
            ndf.append({"PRED_START":prev_from,"PRED_END":prev_to,"DURATION":prev_to - prev_from,"CONFIDENCE":confidence})
            prev_from = row["PRED_START"]
            prev_to = row["PRED_END"]
            confidence = row["CONFIDENCE"]


    ndf.append({"PRED_START":prev_from,"PRED_END":prev_to,"DURATION":prev_to - prev_from,"CONFIDENCE":confidence})

    ndf = pd.DataFrame(ndf)
    return ndf
"""
Prints a formatted version of the prediction to the terminal
"""
def print_predictions(predictions,confidence):
    pred = predictions[["PRED_START","PRED_END","CONFIDENCE"]]
    print(f"\n{pred.to_string(index=False)}")
    print(f"\nFound {len(pred)} events with confidence over {confidence}")

"""
Reads edf file
generates images of the whole signal
runs darknet/yolo on all images, and outputs to predictions.txt
converts predictions to dataframe
outputs to terminal/generates images according to flags set when running program
deletes tmp files
"""
def predict_edf(file,output_png,output_xml,threshold=None,demo=False,replay=False):
    if not threshold:
        threshold = 0

    signal = readEdfFile(file)
    if not replay:
        generate_image_from_signal(signal)

    files = ""
    curdir = os.getcwd()

    for image in glob.iglob(f"tmp{os.sep}*"):
        files += f"{curdir}{os.sep}{image}\n"


    os.chdir("darknet")
    with open("generate.txt","w+") as f:
        f.write(files)

    print("Running YOLO on signal. This may take a long time depending on GPU/CPU and length of recording")
    if not demo and not replay:
        os.system(("./darknet detector test ../obj.data ../yolo-obj.cfg ../yolo-obj_last.weights -ext_output < generate.txt > predictions.txt"))
        pass
    
    print("Done")
    predictions = get_predictions(demo)

    predictions = predictions[predictions.CONFIDENCE > threshold]
    predictions = clean_predictions(predictions)
    apnea_prediction = np.zeros(int(predictions.PRED_END.max()))


    for line in predictions.itertuples():
        for index in range(int(line.PRED_START), int(line.PRED_END)):
            if apnea_prediction[index] < line.CONFIDENCE:
                apnea_prediction[index] = line.CONFIDENCE

    if output_png:
        plot_events(signal,predictions)


    print_predictions(predictions,threshold)
    #Delete the temporary files
    for image in glob.iglob(f"tmp{os.sep}*"):
        os.remove(f"{curdir}{os.sep}{image}")

    os.remove("generate.txt")


if __name__ == "__main__":
    setup()

    parser = argparse.ArgumentParser(description='Predict Apnea events on .edf file ')
    parser.add_argument('file', help='path to a .edf file to analyze')
    parser.add_argument('-p', help='Output png predictions to out/', action="store_true")
    parser.add_argument("-x",'-xml', help='Output predictions annotations to xml file', action="store_true")
    parser.add_argument("-t",'--thresh','-threshold', help='Output predictions annotations to xml file',type=int)

    args = parser.parse_args()
    
    demo = False
    replay = False
    if args.file=="demo":
        print("### DEMO MODE ###")
        print("Uses precalculated predictions for computers without (GPU assisted) darknet.")
        args.file = f"demo/{os.sep}shhs2-200116.edf"
        shutil.copyfile(f"demo/{os.sep}predictions.txt",f"darknet{os.sep}predictions.txt")
        demo=True

    if args.file=="replay":
        print("### Replaying last calculation with new flags ###")
        print("Uses predictions already calculated for creating output")
        args.file = "shhs1-200001.edf"
        replay=True
    
    predict_edf(args.file,output_png=args.p,output_xml=args.p, threshold=args.thresh,demo=demo,replay=replay)
