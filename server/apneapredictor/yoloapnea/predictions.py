import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lxml import etree
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score, roc_curve, auc
from sklearn.preprocessing import binarize
from yattag import Doc, indent

from .apneas import ApneaType
from .evaluate import Evaluate


class Predictions:

    def __init__(self, sliding_window_duration, apnea_types, threshold):
        self._predictions = np.zeros(12 * 60 * 60 * 10)
        self._ground_truth = None
        self._ground_truth_length = 0
        self.sliding_window_duration = sliding_window_duration
        self.last_predicted_index = 0
        self.last_ground_truth_index = 0
        self.apnea_types = apnea_types
        self.threshold = threshold

    @property
    def predictions(self):
        return self._predictions[:self.last_predicted_index]

    @property
    def ground_truth(self):
        if self._ground_truth is None:
            return None
        else:
            return self._ground_truth[:self.ground_truth_length]

    @property
    def ground_truth_length(self):
        return self.last_predicted_index  # Ground truth will never be longer than the signal data

    @property
    def annotation_file(self):
        raise RuntimeError("This property has no getter")

    @annotation_file.setter
    def annotation_file(self, file):

        if type(file) is pd.core.frame.DataFrame:
            self.set_dataFrame_annotations(file)

        elif file.endswith("nsrr.xml"):
            self.read_xml_annotations(file)

        else:
            raise NotImplementedError("Annotation filetype not supported")

    # @property
    # def info(self):
    #     df = self.get_predictions_as_df(self.predictions)
    #     statistics = {}
    #     statistics["apneas"] = len(df["start"])
    #     statistics["recording_length_minutes"] = len(self.predictions) / (60 * 10)  # Hour * hz
    #     statistics["calculated_ahi"] = (statistics["apneas"] / statistics["recording_length_minutes"]) * 60
    #     return statistics

    @property
    def calculatedAhi(self):
        df = self.get_predictions_as_df(self.predictions)
        return len(df["start"]) / (len(self.predictions) / (60 * 10)) * 60

    @property
    def evaluate(self):
        return Evaluate(self.predictions, self.ground_truth, self.apnea_types, self.threshold)

    def get_last_predictions(self):
        """
        Returns an np array of all the last predictions with each index in the array representing a decisecond.
        Will be of size self.sliding_window_duration unless the signal is smaller, then it will be equal
        to the size of the signal
        :return: np array, index in signal of first element in np array
        """

        if self.last_predicted_index >= self.sliding_window_duration:
            start_index = self.last_predicted_index - self.sliding_window_duration
            predictions = self.predictions[start_index: self.last_predicted_index]
        else:
            start_index = 0
            predictions = self.predictions[start_index:self.last_predicted_index]

        return predictions, start_index


    def append_predictions(self, detections, start_index):
        """
        Converts detection object from yolo into timestamps
        and copies the confidence of the prediction into the prediction array

        :param detections: Predictions coming from yolo with values in relative numbers based on
                            the image it was detected on
        :param start_index: index in the signal of the leftmost pixel in the image yolo was run on.
        """

        for detection in detections:
            confidence = detection["confidence"]
            start_percentage = detection["left"]
            end_percentage = detection["right"]

            start = start_index + int(start_percentage * self.sliding_window_duration)
            end = start_index + int(end_percentage * self.sliding_window_duration)

            new_prediction = {"start": start,
                              "end": end,
                              "confidence": confidence}

            self._insert_new_prediction(new_prediction)
        self.last_predicted_index = start_index + self.sliding_window_duration

    def get_xml(self, threshold=0):
        """
        Return NSRR XML of all predictions
        :param threshold: Threshold of yolo's confidence. Discards confidence lower than threshold if thresholds is set.
        :return: string of XML
        """
        doc, tag, text = Doc().tagtext()
        doc.asis('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')

        with tag('PSGAnnotation'):
            with tag('SoftwareVersion'):
                text("Compumedics")
            with tag('EpochLength'):
                text("30")

            with tag("ScoredEvents"):
                start = 0
                for i, confidence in enumerate(self.predictions):
                    if start != 0:
                        if confidence == 0:
                            end = i
                            with tag("ScoredEvent"):
                                with tag("EventType"):
                                    text("Respiratory|Respiratory")
                                with tag("EventConcept"):
                                    text("Obstructive apnea|ObstructiveApnea")
                                with tag("Start"):
                                    text(start)
                                with tag("Duration"):
                                    text(end - start)
                                with tag("SignalLocation"):
                                    text("ABDO RES")
                            start = 0

                    elif confidence > threshold:
                        start = i

        result = indent(
            doc.getvalue(),
            indentation=' ' * 4,
            newline='\r\n'
        )
        return result

    def _insert_new_prediction(self, prediction):
        """
        Inserts prediction into predictions array
        :param prediction: Prediction dictionary with keys: start, end & confidence
        """

        np.maximum(self._predictions[prediction["start"]:prediction["end"]], prediction["confidence"],
                   out=self._predictions[prediction["start"]:prediction["end"]])


    def get_prediction_metrics(self):
        metrics = {}

        metrics["prediction"] = self.get_array_statistics(self.predictions, self.last_predicted_index)

        if self.ground_truth is not None:
            metrics["ground_truth"] = self.get_array_statistics(self.ground_truth, self.ground_truth_length)
            metrics["comparison"] = self.get_evaluation_metrics()

        return metrics

    def read_xml_annotations(self, file):
        self._ground_truth = np.zeros(12 * 60 * 60 * 10)

        with open(file) as f:
            start, end, apnea_type = 0, 0, 0
            tree = etree.parse(f)
            tree = tree.getroot()
            for scored_event in tree.find("ScoredEvents"):
                concept = scored_event.find("EventConcept")
                if concept.text == "Obstructive apnea|Obstructive Apnea":
                    start = int(float(scored_event.find("Start").text))
                    end = start + int(float(scored_event.find("Duration").text))
                    apnea_type = ApneaType.Obstructive.value

                elif concept.text == "Hypopnea|Hypopnea":
                    start = int(float(scored_event.find("Start").text))
                    end = start + int(float(scored_event.find("Duration").text))
                    apnea_type = ApneaType.Hypopnea.value

                self._ground_truth[start:end] = apnea_type

                if concept.text == "Recording Start Time":
                    start = int(float(scored_event.find("Start").text))
                    end = start + int(float(scored_event.find("Duration").text))
                    # self._ground_truth_length = end * 10  # "Duration" is in seconds, converting to deciseconds

    def set_dataFrame_annotations(self, df):
        self._ground_truth = np.zeros(12 * 60 * 60 * 10)
        for row in df.itertuples():
            type = ApneaType[row.type].value
            start = int(row.start * 10)
            end = int(row.end * 10)
            self._ground_truth[start:end] = type
