#!/usr/bin/python3
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
import lxml
from lxml import etree
from io import StringIO, BytesIO
from sklearn.metrics import confusion_matrix, accuracy_score,f1_score,roc_auc_score,classification_report,precision_score,roc_curve
import math
from PIL import Image
from multiprocessing import Pool 
import itertools
import timeit
from src.Prediction import Prediction
from src.config import main_folder

XLIM = 90 * 10
OVERLAP = 45 * 10
out_folder = "out"
tmp_folder = "tmp"


def setup():
    """Checks whether Darknet is installed, creates required folders if needed, 
        and creates a obj.data that works for the current machine
    """
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

    with open("obj.data", "w+") as f:
        f.write(obj_data)

def readEdfFile(file):
    """Reads EDF file from SHHS dataset. Will need adjustments to work for other signals
    
    Arguments:
        file {str} -- Path to edf file
    
    Returns:
        DataFrame -- Dataframe of thorax and abdominal signals, with index in deciseconds since start of recording
    """
    try:
        edf = pyedflib.EdfReader(file)
        cols = edf.getSignalLabels()

        signal = pd.DataFrame([])
        signal['THOR_RES'] = edf.readSignal(cols.index("THOR RES"))
        signal['ABDO_RES'] = edf.readSignal(cols.index("ABDO RES"))
        signal['SUM'] = signal['ABDO_RES'] + signal['THOR_RES']

    finally:
        edf._close()
        del edf

    return signal





def plot_and_write_interval(params):
    signal,start = params
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(start, start + XLIM)
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    ax.set_ylim(-1, 1)
    ax.plot(signal.index, signal["ABDO_RES"])
    fig.savefig(f"tmp/{start}.png")
    plt.close()

    

def generate_image_from_signal(signal):
    """
    Plots images from the signal dataframe in a predictable way. Starts a new image for every OVERLAP/10 seconds to map the whole recording
    """    
    print("Generating image from signal")
    pool = Pool(8)    
    pool.map(plot_and_write_interval,zip([signal for i in range(0, len(signal), OVERLAP)],[i for i in range(0, len(signal), OVERLAP)]))
    print("Generated images")
    
    # TODO Create stats showing how far along we are currently. Probably more optimizing and finetuning?




    """
    Plots the signal of the events that yolo predicted with signal before and after the event

    Returns:
        None -- Outputs prediction images in /out folder
    """
def plot_events(signal, events, annotations=None):


    print("Generating PNG's of all events")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(signal.index, signal["ABDO_RES"])
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Time (Deciseconds)")
    # ax.grid(False)
    #fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    for event in annotations.itertuples():
        ax.plot([event.START, event.END], [-0.8, -0.8], linewidth=3, color="g")
        ax.plot([event.START, event.START],
                [-0.7, -0.9], linewidth=3, color="g")
        ax.plot([event.END, event.END], [-0.7, -0.9], linewidth=3, color="g")

    for line in events.itertuples():

        #marking = ax.axvspan(line.PRED_START, line.PRED_END, alpha=line.CONFIDENCE/100, color='red')
        ax.plot([line.PRED_START, line.PRED_END],
                [-0.6, -0.6], linewidth=3, color="r")
        ax.plot([line.PRED_START, line.PRED_START],
                [-0.5, -0.7], linewidth=3, color="r")
        ax.plot([line.PRED_END, line.PRED_END],
                [-0.5, -0.7], linewidth=3, color="r")
        ax.text(line.PRED_START-20, -0.75, line.PRED_START, family="serif")
        ax.text(line.PRED_END-20, -0.75, line.PRED_END, family="serif")

        # marking.remove()

    with progressbar.ProgressBar(max_value=len(events)) as event:
        i = 0
        for line in events.itertuples():
            ax.set_xlim(line.PRED_START-400, line.PRED_END + 400)

            event.update(i)
            i += 1
            #extra = Rectangle((0, 0), 1, 1, fc="w", fill=False,
            #                  edgecolor='none', linewidth=0)
            leg = ax.legend([f"Prediction of apnea", f"Start = {line.PRED_START}",
                             f"End = {line.PRED_END}", f"Confidence = {line.CONFIDENCE}"], loc="upper right")
            leg._legend_box.align = "right"
            fig.savefig(f"../out/{line.PRED_START}.png")

    print("Done creating png files. See out/ for output")


"""


Returns:
    Dataframe -- Dataframe with info about when the image starts,when the prediction starts, when the prediction ends, and confidence in prediction
"""


def get_predictions(demo):
    """Analyses predictions.txt to convert yolos prediction to a dataframe for easier processing
converts pixelvalues from prediction to correct event-time since start of recording
    
    Arguments:
        demo {bool} -- if True then use already calculated demo file  
    
    Returns:
        DataFrame -- Prediction of all apnea events saved in ./predictions.txt file
    """
    
    print("Analyses predictions")
    
    predictions = []
    image_width = Image.open("../tmp/0.png").size[0]
    pixel_duration = image_width/XLIM

    predictions_file = "./predictions.txt"
    
    if demo:
        predictions_file = "../demo/predictions.txt"

    with open(predictions_file, "r") as f:
        for line in f:
            line = line[0:-1]
            new_image = re.search(r"tmp\/(\d+).png:", line)
            if new_image:
                start_value = int(new_image.group(1))
            new_apnea = re.search(
                r"apnea:\D(\d+)%.*left_x:\D*(\d+).*width:\D*(\d+)", line)
            if new_apnea:
                confidence = int(new_apnea.group(1))
                apnea_start = start_value + \
                    (int(new_apnea.group(2)) / pixel_duration)
                apnea_width = apnea_start + \
                    (int(new_apnea.group(3)) / pixel_duration)
                predictions.append({'IMG_START': start_value, "PRED_START": apnea_start,
                                    "PRED_END": apnea_width, "CONFIDENCE": confidence})
    return pd.DataFrame(predictions)


def clean_predictions(predictions,length):
    predictions = predictions.sort_values(by=["PRED_START"])
    ndf = []

    prev_to = -1
    prev_from = 0
    confidence = 200
    for index, row in predictions.iterrows():
        if prev_to == -1:
            prev_from = row.PRED_START
            prev_to = row.PRED_END
            confidence = row.CONFIDENCE

        elif row.PRED_START <= prev_from and row.PRED_END> prev_to:
            prev_from = row.PRED_START
            prev_to = row.PRED_END
            confidence = confidence if row.CONFIDENCE> confidence else row.CONFIDENCE

        elif row.PRED_START > prev_from and row.PRED_END < prev_to:
            pass
        elif row.PRED_START <= prev_to and row.PRED_END > prev_to:
            prev_to = row.PRED_END
            confidence = confidence if row.CONFIDENCE > confidence else row.CONFIDENCE

        else:
            confidence = confidence if row.CONFIDENCE > confidence else row.CONFIDENCE
            ndf.append({"PRED_START": prev_from, "PRED_END": prev_to,
                        "DURATION": prev_to - prev_from, "CONFIDENCE": confidence})
            prev_from = row.PRED_START
            prev_to = row.PRED_END
            confidence = row["CONFIDENCE"]

    prev_to = prev_to if prev_to < length else length
    
    ndf.append({"PRED_START": prev_from, "PRED_END": prev_to,
                "DURATION": prev_to - prev_from, "CONFIDENCE": confidence})
    
    ndf = pd.DataFrame(ndf)
    return ndf


"""
Prints a formatted version of the prediction to the terminal
"""


def print_predictions(predictions, confidence):
    """Prints a formatted version of predictions to the terminal
    
    Arguments:
        predictions {dataFrame} -- All predictions
        confidence {int} -- confidence value used on dataframe to filer away low confidence events
    """
    pred = predictions[["PRED_START", "PRED_END", "CONFIDENCE", "DURATION"]]
    print(f"\n{pred.to_string(index=False)}")
    print(f"\nFound {len(pred)} events with confidence over {confidence}")


def convert_events_to_array(events, length):
    """Converts dataframe of events to array of 0,1 with 1 being an event, and 0 being non-event
    
    Arguments:
        events {DataFrame} -- All events with start and end
        length {int} -- Length of the recorded sleep
    
    Returns:
        int array -- array consisting of 1 and 0. 1 is event, 0 is not-event
    """

    values = np.zeros(length)

    for line in events.itertuples():
        if "START" in events:
            for index in range(int(line.START), int(line.END)):
                values[index] = 1
        else:
            for index in range(int(line.PRED_START), int(line.PRED_END)):
                values[index] = 1
    return values

def get_metrics_of_prediction(truth,pred):
    print("Getting metrics")
    print("Precision Score")
    precision = precision_score(truth,pred)
    print(precision)

    print("Confusion matrix")
    confusion = confusion_matrix(truth,pred)
    print(confusion)
    
    print("Classification_report")
    report = classification_report(truth,pred)
    print(report)
    
    print("ROC_AUC")
    auc_roc = roc_auc_score(truth,pred)
    print(auc_roc)
    


def get_accuracy(tn, fp, fn, tp, threshold, length=False, total_predicted_events=None, total_annotated_events=None):
    """Predicts different versions of accuracy and precission
    
    Arguments:
        tn {int} -- Number of True Negatives
        fp {int} -- Number of True Positives
        fn {int} -- Number of False Negatives
        tp {int} -- Number of True Positives
        threshold {int} -- What threshold was used in filtering the dataset
    
    Keyword Arguments:
        length {int} -- Length of sleep recording (default: {False})
        total_predicted_events {int} -- Number of predicted events (default: {None})
        total_annotated_events {int} -- Number of true events annotated (default: {None})
    
    Returns:
        Dataframe -- Dataframe of different predictions
    """
    datapoint_results = {}

    datapoint_results["FALSE_POSITIVE_COUNT"] = fp
    datapoint_results["FALSE_NEGATIVE_COUNT"] = fn
    datapoint_results["TRUE_POSITIVE_COUNT"] = tp
    datapoint_results["SENSITIVITY"] = (tp/(tp+fn))*100
    datapoint_results["PRECISION"] = (tp/(tp+fp))*100
    datapoint_results["THRESHOLD"] = threshold
    if tn:
        datapoint_results["TRUE_NEGATIVE_COUNT"] = tn
        datapoint_results["SPECIFICITY"] = (tn/(tn+fp))*100
        datapoint_results["ACCURACY"] = ((tp+tn)/(fp+tn+tp+fn))*100
        datapoint_results["NPV"] = (tn/(tn+fn))*100

    if length:
        deciseconds_to_hours_ratio = 36000
        sleep_in_hours = length / deciseconds_to_hours_ratio
        datapoint_results["AHI_PREDICTED"] = total_predicted_events / \
            sleep_in_hours
        datapoint_results["AHI_TRUE"] = total_annotated_events/sleep_in_hours
    datapoint_results = pd.Series(datapoint_results)
    return datapoint_results


def event_confusion_matrix(annotations, predictions, annotation_truths, apnea_prediction):
    """Finds values for a confusion matrix similar to skikit.confusion_matrix, but on events instead(events are apneas)
    
    Arguments:
        annotations {DataFrame} -- Ground truth  timeannotations 
        predictions {DataFrame} -- Predicted time of events
        annotation_truths {int array} -- Array representation of annotations. 1 is apnea, 0 is non-apnea
        apnea_prediction {int array} -- Array representation of prediction. 1 is predicted apnea, 0 is predicted non-apnea
    
    Returns:
        tupple -- tn,tp,fn,pf. Currently tn is None because calculations may give wrong impression of accuracy
    """
    tn, tp, fn, fp = None, 0, 0, 0

    for line in annotations.itertuples():
        if np.isin(1, apnea_prediction[int(line.START):int(line.END)]):
            tp += 1
        else:
            fn += 1

    for line in predictions.itertuples():
        if np.isin(1, annotation_truths[int(line.PRED_START):int(line.PRED_END)]):
            pass
        else:
            fp += 1
    return (tn, tp, fn, fp)


def compare_prediction_to_annotation(predictions, annotations, threshold, length):
    """Compares the predictions to the ground truth from the annotations

    Arguments:
        predictions {DataFrame} -- Predicted event
        annotations {DataFrame} -- Annotated events
        threshold {int}-- threshold used for fitlering out predictions
        length {int} -- length of sleep in deciseconds

    Returns:
        DataFrame -- Dataframe of values in both binary form and event form
    """

    annotation_truths = convert_events_to_array(annotations, length)
    apnea_prediction = convert_events_to_array(predictions, length)

    # For datapoints

    tn, fp, fn, tp = confusion_matrix(annotation_truths, apnea_prediction).ravel()
    datapoint_results = get_accuracy(tn, fp, fn, tp, threshold)

    get_metrics_of_prediction(annotation_truths,apnea_prediction)
    # For events
    tn, fp, fn, tp = event_confusion_matrix(
        annotations, predictions, annotation_truths, apnea_prediction)
    
    event_results = get_accuracy(tn, fp, fn, tp, threshold, length=length, total_predicted_events=len(
        predictions), total_annotated_events=len(annotations))
    
    results_df = pd.DataFrame({"Datapoints": datapoint_results, "Events": event_results},
                              index=["FALSE_POSITIVE_COUNT", "TRUE_POSITIVE_COUNT", "TRUE_NEGATIVE_COUNT", "FALSE_NEGATIVE_COUNT", "SENSITIVITY", "PRECISION",
                                     "SPECIFICITY", "ACCURACY", "NPV", "AHI_PREDICTED", "AHI_TRUE", "THRESHOLD"])
    return results_df






def predict_edf(file, output_png, output_xml, threshold=0, demo=False, replay=False, compare=None, display=False, plot_comp=False):
    """Reads edf file
    generates images of the whole signal
    runs darknet/yolo on all images, and outputs to predictions.txt
    converts predictions to dataframe
    outputs to terminal/generates images according to flags set when running program
    deletes tmp files
    
    Arguments:
        file {str} -- File path
        output_png {bool} -- Whether to output png or not
        output_xml {bool} -- Whether to output xml or not
    
    Keyword Arguments:
        threshold {int} -- threshold to filter predictions at (default: {None})
        demo {bool} -- if true then use calculated weight instead of generating new (default: {False})
        replay {bool} -- Use last predictions again (default: {False})
        compare {str} -- string to annotation file to compare agains(default: {None})
        display {bool} -- enable to print to terminal (default: {False})
        plot_comp {bool} -- Enable to plot results of multiple prediction thresholds (default: {False})
    """
    files = ""
    curdir = os.getcwd()


    signal = readEdfFile(file)
    length = len(signal)
    if not replay:

        # Delete the previous tmp files
        for f in glob.iglob(f"tmp{os.sep}*"):
            os.remove(f"{curdir}{os.sep}{f}")
        shutil.copyfile(file, f"tmp{os.sep}last_file.edf")

        generate_image_from_signal(signal)

    for image in glob.iglob(f"tmp{os.sep}*.png"):
        files += f"{curdir}{os.sep}{image}\n"

    os.chdir("darknet")
    with open("generate.txt", "w+") as f:
        f.write(files)

    if not demo and not replay:
        print("Running YOLO on signal. This may take a long time depending on GPU/CPU and length of recording")
        os.system(("./darknet detector test ../obj.data ../yolo-obj.cfg ../yolo-obj_last.weights -dont_show -ext_output < generate.txt > predictions.txt"))
        print("Done")

    predictions = get_predictions(demo)
    if plot_comp:
        threshold = 0
    else:
        predictions = predictions[predictions.CONFIDENCE >= threshold]

    predictions = clean_predictions(predictions,length)
    annotations = None

    if compare:
        print(f"\nComparing to {compare}")
        annotations = read_annotation_file(compare)

        if plot_comp:
            print("plot_comp")
            results = pd.DataFrame()
            for i in range(0, 101, 1):

                predictions = predictions[predictions.CONFIDENCE >= i]
                values = compare_prediction_to_annotation(
                    predictions, annotations, i, length)
                if values is not None:
                    values.name = i
                    results = results.append(values)
            print(results)
            fig, ax = plt.subplots(figsize=(20, 20))
            #ax.plot(results.ACCURACY_RESULT*100,label="Total accuracy")
            ax.plot(results.EVENTS_FOUND, label="Events found")
            ax.plot(results.EVENTS_NOT_FOUND, label="Events not found")
            ax.plot(results.NON_APNEA_EVENTS_PREDICTED,
                    label="Non apnea predicted")

            ax.legend()
            plt.show()
        else:
            results = compare_prediction_to_annotation(
                predictions, annotations, threshold, length)
            print(results.round(2))

    if output_png:
        plot_events(signal, predictions, annotations)

    if display:
        print_predictions(predictions, threshold)

    os.remove("generate.txt")


if __name__ == "__main__":
    """Argparser to set coorect values for further processing
    """
    setup()

    parser = argparse.ArgumentParser(
        description='Predict Apnea events on .edf file ')
    parser.add_argument('file', help='path to a .edf file to analyze')
    parser.add_argument(
        '-p', help='Output png predictions to out/', action="store_true")
    parser.add_argument(
        "-x", '-xml', help='Output predictions annotations to xml file', action="store_true")
    parser.add_argument("-t", '--thresh', '-threshold',
                        help='Change threshold for keeping prediction', type=int,default=0)
    parser.add_argument("-c", '--compare', help='Compare to annotation file')
    parser.add_argument(
        "-d", '--display', help='Display predictions to screen', action="store_true")
    parser.add_argument(
        '--plot_comparisons', help='Only with -c flag. Plots accuracy at different values', action="store_true")

    args = parser.parse_args()

    demo = False
    replay = False
    if args.file == "demo":
        print("### DEMO MODE ###")
        print(
            "Uses precalculated predictions for computers without (GPU assisted) darknet.")
        args.file = f"demo{os.sep}shhs2-200116.edf"
        shutil.copyfile(f"demo{os.sep}predictions.txt",
                        f"darknet{os.sep}predictions.txt")
        demo = True

    if args.file == "replay":
        print("### Replaying last calculation with new flags ###")
        print("Uses predictions already calculated for creating output")
        args.file = f"tmp{os.sep}last_file.edf"
        replay = True
    
    signal_path = f"{os.getcwd()}{os.sep}{args.file}"
    annotation_path = f"{os.getcwd()}{os.sep}{args.compare}"
    
    generate_reports = False
    if generate_reports:
        #patients =["shhs1-202105"]
        patients = ["shhs1-202105",
                    "shhs2-204782",
                    "shhs2-200353",
                    "shhs1-203654",
                    "shhs1-201723",
                    "shhs1-200824",
                    "shhs2-204583",
                    "shhs1-202496",
                    "shhs2-204798",
                    "shhs1-201758"]
        results = {}
        

        for patient in patients:
            prediction = Prediction(patient,annotation_path=patient,replay=replay,demo=demo,threshold=args.thresh)
            results[patient] = prediction.get_predictions()
            #results[patient] = prediction.report_full()
            print("patient filename")
            print(patient)
            print (f"{main_folder}{patient}")
            results[patient].to_csv(f"{main_folder}{patient}.csv")
        
        for a,b in results.items():
            print()
            print(a)
            print(b)
    else:
        print(args.file)
        prediction = Prediction(args.file,annotation_path=args.compare,replay=replay,demo=demo,threshold=args.thresh)
        results = prediction.get_predictions()
        print(results)

    #predict_edf(args.file, output_png=args.p, output_xml=args.p, threshold=args.thresh, demo=demo,
    #            replay=replay, compare=args.compare, display=args.display, plot_comp=args.plot_comparisons)
