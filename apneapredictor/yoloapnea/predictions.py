import pickle

import numpy as np
import pandas as pd
from lxml import etree
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score
from sklearn import preprocessing
from sklearn.preprocessing import binarize

from yattag import Doc, indent

from .config import ImageConfig


class Predictions:

    def __init__(self):
        self.predictions = np.zeros(12 * 60 * 60 * 10)
        self.ground_truth = None
        self.ground_truth_length = 0
        self.sliding_window_duration = ImageConfig.sliding_window_duration
        self.last_predicted_index = 0

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

    def get_predictions_as_np_array(self):
        """
        All stored predictions as numpy array
        :return: numpy array of predictions. Values represent confidence of prediction. 0 < value < 1
        """
        return self.predictions

    def get_predictions_as_df(self, predictions):

        # with open('predictions_whole_recording.npy', 'wb') as f:
        #     np.save(f,self.predictions)

        # Taken from
        # https://stackoverflow.com/questions/49491011/python-how-to-find-event-occurences-in-data
        indicators = (predictions > 0.0).astype(int)
        indicators_diff = np.concatenate(
            [[0], indicators[1:] - indicators[:-1]])
        diff_locations = np.where(indicators_diff != 0)[0]

        assert len(diff_locations) % 2 == 0

        starts = diff_locations[0::2]
        ends = diff_locations[1::2]

        df = pd.DataFrame({'start': starts,
                           'end': ends, })

        df['min_confidence'] = [predictions[start:end].min()
                                for start, end in zip(df["start"], df["end"])]
        df['max_confidence'] = [predictions[start:end].max()
                                for start, end in zip(df["start"], df["end"])]
        df['duration'] = df["end"] - df["start"]
        return df

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

            start = start_index + \
                int(start_percentage * self.sliding_window_duration)
            end = start_index + int(end_percentage *
                                    self.sliding_window_duration)

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

        np.maximum(self.predictions[prediction["start"]:prediction["end"]], prediction["confidence"],
                   out=self.predictions[prediction["start"]:prediction["end"]])

        print()

    def get_prediction_metrics(self):
        print("Getting prediction metrics")
        df = self.get_predictions_as_df(self.predictions)
        metrics = {}
        prediction_metrics = {}
        annotation_metrics = {}

        prediction_metrics["event_count"] = len(df["start"])
        prediction_metrics["mean_duration"] = df["duration"].mean() if len(
            df["start"]) > 0 else 0
        # Hour * hz
        prediction_metrics["recording_length_minutes"] = self.last_predicted_index / (
            60 * 10)
        if prediction_metrics["recording_length_minutes"] > 0:
            prediction_metrics["calculated_ahi"] = (
                prediction_metrics["event_count"] / prediction_metrics["recording_length_minutes"]) * 60

        metrics["prediction"] = prediction_metrics

        if self.ground_truth is not None:
            df = self.get_predictions_as_df(self.ground_truth)

            annotation_metrics["event_count"] = len(df["start"])
            annotation_metrics["mean_duration"] = df["duration"].mean() if len(
                df["start"]) > 0 else 0

            annotation_metrics["annotation_length_minutes"] = self.ground_truth_length / (
                60 * 10)
            metric_end = int(
                float(max(self.ground_truth_length, self.last_predicted_index)))

            if annotation_metrics["annotation_length_minutes"] > 0:
                annotation_metrics["calculated_ahi"] = (annotation_metrics["event_count"] / annotation_metrics[
                    "annotation_length_minutes"]) * 60

            predictions = self.predictions[:metric_end]
            ground_truth = self.ground_truth[:metric_end]
            ground_truth_binary = np.ravel(
                binarize(ground_truth.reshape(1, -1), 0))
            predictions_binary = np.ravel(
                binarize(predictions.reshape(1, -1), 0))

            annotation_metrics["accuracy_score"] = accuracy_score(
                ground_truth_binary, predictions_binary)
            annotation_metrics["f1_score"] = f1_score(
                ground_truth_binary, predictions_binary)
            annotation_metrics["precision_score"] = precision_score(
                ground_truth_binary, predictions_binary)
            annotation_metrics["recall_score"] = recall_score(
                ground_truth_binary, predictions_binary)

            metrics["annotation"] = annotation_metrics

        return metrics

    def read_xml_annotations(self, file):
        print("reading XML annotations")
        self.ground_truth = np.zeros(12 * 60 * 60 * 10)

        with open(file) as f:
            start, end, apnea_type = 0, 0, 0
            tree = etree.parse(f)
            tree = tree.getroot()
            for scored_event in tree.find("ScoredEvents"):
                concept = scored_event.find("EventConcept")
                if concept.text == "Obstructive apnea|Obstructive Apnea":
                    start = int(float(scored_event.find("Start").text))
                    end = start + \
                        int(float(scored_event.find("Duration").text))
                    apnea_type = 1

                elif concept.text == "Hypopnea|Hypopnea":
                    start = int(float(scored_event.find("Start").text))
                    end = start + \
                        int(float(scored_event.find("Duration").text))
                    apnea_type = 2

                self.ground_truth[start:end] = apnea_type

                if concept.text == "Recording Start Time":
                    start = int(float(scored_event.find("Start").text))
                    end = start + \
                        int(float(scored_event.find("Duration").text))
                    self.ground_truth_length = end
