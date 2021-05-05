import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, precision_score
from sklearn.metrics import f1_score, recall_score, matthews_corrcoef

from .apneas import ApneaType


class Evaluate:

    def __init__(self, predictions, ground_truth, apnea_types, threshold):
        self.predictions = predictions
        self.predictionsBool = predictions > threshold
        self.ground_truth = np.isin(ground_truth, [apnea.value for apnea in apnea_types])
        self.threshold = threshold

    @property
    def scores(self):
        return {
            "f1": self.f1,
            "confusion_matrix": self.confusion_matrix,
            "roc_curve": self.roc_curve,
            "auc": self.auc,
            "accuracy": self.accuracy,
            "ahi": self.ahi,
            "precision": self.precision,
            "recall": self.recall,
            "tp_apneas": self.tp_apneas,
            "fp_apneas": self.fp_apneas,
            "fn_apneas": self.fn_apneas,
            "MCC": self.mcc
        }

    @property
    def f1(self):
        return f1_score(self.ground_truth, self.predictionsBool)

    @property
    def confusion_matrix(self):

        tn, fp, fn, tp = confusion_matrix(self.ground_truth, self.predictionsBool).ravel()
        return {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp
        }

    @property
    def roc_curve(self):
        fpr, tpr, thresholds = roc_curve(self.ground_truth, self.predictions, pos_label=1)
        return {
            "fpr": fpr,
            "tpr": tpr,
            "tresholds": thresholds
        }

    @property
    def auc(self):
        roc_curve = self.roc_curve
        fpr = roc_curve["fpr"]
        tpr = roc_curve["tpr"]
        return auc(fpr, tpr)

    @property
    def accuracy(self):
        return accuracy_score(y_true=self.ground_truth, y_pred=self.predictionsBool)

    @property
    def ahi(self):
        return {
            "prediction_AHI": self.predictionAHI,
            "true_AHI": self.groundTruthAHI
        }

    @property
    def precision(self):
        return precision_score(self.ground_truth, self.predictionsBool)

    @property
    def recall(self):
        return recall_score(self.ground_truth, self.predictionsBool)

    @property
    def predictionAHI(self):
        df = self.get_predictions_as_df(self.predictions)
        return len(df["start"]) / (len(self.predictions) / (60 * 10)) * 60

    @property
    def groundTruthAHI(self):
        df = self.get_predictions_as_df(self.ground_truth)
        return len(df["start"]) / (len(self.ground_truth) / (60 * 10)) * 60

    @property
    def tp_apneas(self):
        in_apnea = False
        predicted_current_apnea = False
        tp = 0
        for gt, pd in zip(self.ground_truth, self.predictionsBool):
            if not in_apnea and gt == False:
                continue
            elif in_apnea and gt == False:
                in_apnea = False
                if predicted_current_apnea:
                    tp += 1
                predicted_current_apnea = False

            elif in_apnea and gt == True:
                if pd:
                    predicted_current_apnea = True
            elif not in_apnea and gt == True:
                in_apnea = True

                if pd:
                    predicted_current_apnea = True
        if predicted_current_apnea and in_apnea:
            tp += 1
        return tp

    @property
    def fp_apneas(self):
        fp = 0
        in_predicted_apnea = False
        ground_truth_in_predicted = False
        for gt, pd in zip(self.ground_truth, self.predictionsBool):
            if not in_predicted_apnea and pd == False:
                continue
            elif not in_predicted_apnea and pd == True:

                in_predicted_apnea = True
                if gt == True:
                    ground_truth_in_predicted = True

            elif in_predicted_apnea and pd == True:

                if gt == True:
                    ground_truth_in_predicted = True
            elif in_predicted_apnea and pd == False:

                if ground_truth_in_predicted:
                    ground_truth_in_predicted = False
                else:
                    fp += 1
                in_predicted_apnea = False
        if not ground_truth_in_predicted and in_predicted_apnea:
            fp += 1
        return fp

    @property
    def fn_apneas(self):
        in_apnea = False
        predicted_this_apnea = False
        fn = 0
        for gt, pd in zip(self.ground_truth, self.predictionsBool):
            if gt and in_apnea:
                if pd:
                    predicted_this_apnea = True
            elif gt and not in_apnea:
                in_apnea = True
                if pd:
                    predicted_this_apnea = True
            elif not gt and in_apnea:
                in_apnea = False
                if not predicted_this_apnea:
                    fn += 1
            elif not gt and not in_apnea:
                predicted_this_apnea = False

        if in_apnea and not predicted_this_apnea:
            fn += 1

        return fn

    @property
    def mcc(self):
        return matthews_corrcoef(self.ground_truth, self.predictionsBool)

    def get_predictions_as_df(self, predictions):

        indicators = (predictions > self.threshold).astype(int)

        in_event = False
        starts = []
        ends = []

        for i, val in enumerate(indicators):
            if val == True and not in_event:
                starts.append(i)
                in_event = True
            elif val == False and in_event:
                ends.append(i)
                in_event = False

        if in_event:
            ends.append(len(indicators))

        df = pd.DataFrame({'start': starts,
                           'end': ends, })

        df['min_confidence'] = [predictions[start:end].min() for start, end in zip(df["start"], df["end"])]
        df['max_confidence'] = [predictions[start:end].max() for start, end in zip(df["start"], df["end"])]
        df['duration'] = df["end"] - df["start"]
        return df
