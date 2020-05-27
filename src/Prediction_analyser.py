from src.config import tmp_dir,XLIM,predictions_file_name,darknet_dir
from PIL import Image
import re
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score,f1_score,roc_auc_score,classification_report,precision_score,roc_curve

class Prediction_analyser:
    
    def __init__(self,predictions_file,recording):
        self.predictions_file = predictions_file
        self.predictions = self.get_predictions()
        self.recording = recording
        self.length = self.recording.length
        

        
    
    def convert_events_to_array(self,events):
        """Converts dataframe of events to array of 0,1 with 1 being an event, and 0 being non-event
        
        Arguments:
            events {DataFrame} -- All events with start and end
            length {int} -- Length of the recorded sleep
        
        Returns:
            int array -- array consisting of 1 and 0. 1 is event, 0 is not-event
        """

        values = np.zeros(self.length)

        for line in events.itertuples():
            if "START" in events:
                for index in range(int(line.START), int(line.END)):
                    values[index] = 1
            else:
                for index in range(int(line.PRED_START), int(line.PRED_END)):
                    values[index] = 1
        return values
    
    def get_metrics_of_prediction(self,truth,pred):
        class_report = classification_report(truth,pred,output_dict=True,target_names=["non-apnea","apnea"])
        macro_avg_report = class_report["apnea"]    
        return macro_avg_report
        
    def event_confusion_matrix(self,annotations, predictions, annotation_truths, apnea_prediction):
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
        
    
    def deciseconds_to_hours(self,deciseconds):
        return deciseconds/10/60/60
    
    def get_report(self,threshold=0):
        annotations = self.recording.annotation.annotations
        predictions = self.clean_predictions(threshold)
        
        annotation_truths = self.convert_events_to_array(annotations)
        apnea_prediction = self.convert_events_to_array(predictions)

        metrics = self.get_metrics_of_prediction(annotation_truths,apnea_prediction)
        
        metrics["ahi_true"] = len(annotations) / self.deciseconds_to_hours(self.length)
        metrics["ahi_predicted"] = len(predictions) / self.deciseconds_to_hours(self.length)
        df = pd.Series(metrics)
        return df

    def get_report_from_multiple_thresholds(self):
        thresholds = [20,30,35,40,45,50,55,60,70,80,90,95,97,99]
        #thresholds = [20,50]
        report = {}
        for t in thresholds:
            report[str(t)] = self.get_report(t)
        df = pd.DataFrame(report)
        df = df.rename_axis('THRESHOLDS', axis='columns')
        return df
        
 
        
    def get_predictions(self):
        """Analyses predictions.txt to convert yolos prediction to a dataframe for easier processing
            converts pixelvalues from prediction to correct event-time since start of recording
        
        Returns:
            DataFrame -- Prediction of all apnea events saved in ./predictions.txt file
        """
        
        print("Analyses predictions")
        
        predictions = []
        image_width = Image.open(f"{tmp_dir}0.png").size[0]
        pixel_duration = image_width/XLIM

        predictions_file = f"{darknet_dir}{predictions_file_name}"

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
    
    
    def clean_predictions(self,threshold):
        predictions = self.predictions.sort_values(by=["PRED_START"])
        predictions = predictions[predictions.CONFIDENCE >= threshold]

        ndf = []

        prev_to = -1
        prev_from = 0
        confidence = 200
        for _, row in predictions.iterrows():
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

        prev_to = prev_to if prev_to < self.length else self.length
        
        ndf.append({"PRED_START": prev_from, "PRED_END": prev_to,
                    "DURATION": prev_to - prev_from, "CONFIDENCE": confidence})
        
        ndf = pd.DataFrame(ndf)
        return ndf
    
    