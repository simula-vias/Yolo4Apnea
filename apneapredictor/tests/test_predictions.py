import numpy as np
import os
import pprint
from unittest import TestCase
from xml.dom import minidom
from yoloapnea.apneas import ApneaType
from yoloapnea.predictions import Predictions


class TestPredictions(TestCase):

    def setUp(self):
        self.sliding_window_duration = 900

        apneaTypes = [ApneaType.Obstructive]
        self.predictions = Predictions(self.sliding_window_duration, apneaTypes, 0.25)

        self.non_overlap_predictions = [{"left": 0.2,
                                         "right": 0.4,
                                         "confidence": 70},
                                        {"left": 0.5,
                                         "right": 0.7,
                                         "confidence": 65}]

        self.overlap_predictions = [{"left": 0.2,
                                     "right": 0.6,
                                     "confidence": 70},
                                    {"left": 0.5,
                                     "right": 0.7,
                                     "confidence": 65}]

    def test_insert_new_prediction(self):
        first_prediction = {"start": 30,
                            "end": 400,
                            "confidence": 70}
        self.predictions._insert_new_prediction(first_prediction)

        second_prediction = {"start": 450,
                             "end": 700,
                             "confidence": 65}
        self.predictions._insert_new_prediction(second_prediction)
        self.predictions.last_predicted_index = second_prediction["start"] + self.sliding_window_duration
        pred_array = self.predictions.predictions

        self.assertEqual(pred_array[29], 0)
        self.assertEqual(pred_array[30], 70)
        self.assertEqual(pred_array[200], 70)
        self.assertEqual(pred_array[399], 70)
        self.assertEqual(pred_array[400], 0)
        self.assertEqual(pred_array[401], 0)

        self.assertEqual(pred_array[420], 0)
        self.assertEqual(pred_array[449], 0)
        self.assertEqual(pred_array[450], 65)
        self.assertEqual(pred_array[451], 65)
        self.assertEqual(pred_array[563], 65)
        self.assertEqual(pred_array[699], 65)
        self.assertEqual(pred_array[700], 0)
        self.assertEqual(pred_array[800], 0)

    def test_get_last_predictions_no_data(self):
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), 0)
        self.assertEqual(start_index, 0)

    def test_get_last_predictions_with_some_data(self):
        self.predictions.append_predictions(self.non_overlap_predictions, -int(self.sliding_window_duration * 0.3))
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration * 0.7)
        self.assertEqual(start_index, 0)

    def test_get_last_predictions_with_enough_data(self):
        self.predictions.append_predictions(self.non_overlap_predictions, int(self.sliding_window_duration * 3))
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)
        self.assertEqual(start_index, self.sliding_window_duration * 3)

    def test_get_last_predictions_with_adding_data(self):
        self.predictions.append_predictions(self.non_overlap_predictions, 0)
        last_pred, start_index = self.predictions.get_last_predictions()

        self.assertEqual(len(last_pred), self.sliding_window_duration)
        self.predictions.append_predictions(self.non_overlap_predictions, 200)

        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 400)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 500)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 700)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 900)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 950)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

        self.predictions.append_predictions(self.non_overlap_predictions, 1200)
        last_pred, start_index = self.predictions.get_last_predictions()
        self.assertEqual(len(last_pred), self.sliding_window_duration)

    def test_append_predictions(self):
        self.predictions.append_predictions(self.non_overlap_predictions, 0)
        pred_array = self.predictions.predictions

        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.2)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.199)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.23)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.39)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.40)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.41)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.47)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.5)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.499)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.51)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.699)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.7)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.85)], 0)

    def test_append_predictions_with_overlap(self):
        self.predictions.append_predictions(self.overlap_predictions, 0)
        pred_array = self.predictions.predictions

        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.2)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.199)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.23)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.39)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.40)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.41)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.47)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.59)], 70)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.6)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.61)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.699)], 65)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.7)], 0)
        self.assertEqual(pred_array[int(self.sliding_window_duration * 0.85)], 0)

    def test_get_xml(self):
        self.predictions.append_predictions(self.non_overlap_predictions, 0)

        xml = self.predictions.get_xml(0)
        minidom.parseString(xml)

    # def test_get_predictions_as_df(self):
    #     self.predictions.append_predictions(self.non_overlap_predictions, 0)
    #     df = self.predictions.get_predictions_as_df(self.predictions.predictions)
    #
    #     self.assertTrue(self.sliding_window_duration * 0.2 in df["start"].values)
    #     self.assertTrue(self.sliding_window_duration * 0.4 in df["end"].values)
    #
    #     self.assertFalse(self.sliding_window_duration * 0.1 in df["start"].values)
    #     self.assertFalse(self.sliding_window_duration * 0.1 in df["end"].values)
    #
    #     self.assertFalse(self.sliding_window_duration * 0.45 in df["start"].values)
    #     self.assertFalse(self.sliding_window_duration * 0.35 in df["end"].values)
    #
    #     self.assertTrue(self.sliding_window_duration * 0.5 in df["start"].values)
    #     self.assertTrue(self.sliding_window_duration * 0.7 in df["end"].values)

    # def test_get_prediction_metrics(self):
    #     self.predictions.append_predictions(self.non_overlap_predictions, 0)
    #     metrics = self.predictions.get_prediction_metrics()
    #     self.assertIsNotNone(metrics)
    #     self.assertIn("prediction", metrics)
    #     prediction_metrics = metrics["prediction"]
    #     self.assertIn("event_count", prediction_metrics)
    #     self.assertIn("mean_duration", prediction_metrics)
    #     self.assertIn("recording_length_minutes", prediction_metrics)
    #     self.assertIn("calculated_ahi", prediction_metrics)
    #
    #     self.assertTrue(prediction_metrics["event_count"], 2)
    #     self.assertTrue(prediction_metrics["recording_length_minutes"], 900 / 10 / 60)

    def test_read_xml_annotations(self):
        file = f"{os.getcwd()}{os.sep}shhs1-200002-nsrr.xml"
        self.predictions.read_xml_annotations(file)
        self.predictions.last_predicted_index = 10000
        self.assertTrue(self.predictions.ground_truth.max() != 0)
        self.assertTrue(self.predictions.ground_truth[8717] == 1)
        self.assertTrue(self.predictions.ground_truth[8716] == 1)
        self.assertTrue(self.predictions.ground_truth[8715] == 0)
        self.assertTrue(self.predictions.ground_truth[3039] == 2)
        self.assertTrue(self.predictions.ground_truth[3036] == 0)

    def test_set_annotation_dataframe(self):
        file = f"{os.getcwd()}{os.sep}200020.npz"
        with np.load(file, allow_pickle=True) as p:
            data = p["data"].item()
            annotation_df = data["shhs1"]["annotation"]
            self.predictions.annotation_file = annotation_df
            self.assertEqual(self.predictions.ground_truth_length, self.predictions.last_predicted_index)
            self.predictions.append_predictions(self.non_overlap_predictions, 0)
            self.assertEqual(self.sliding_window_duration, self.predictions.last_predicted_index)

    # def test_get_prediction_metrics_compared_to_annotations(self):
    #     file = f"{os.getcwd()}{os.sep}shhs1-200002-nsrr.xml"
    #     self.predictions.append_predictions(self.overlap_predictions, 0)
    #     self.predictions.read_xml_annotations(file)
    #     metrics = self.predictions.get_prediction_metrics()
    #     self.assertTrue("comparison" in metrics)
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(metrics)

    # def test_plot_roc(self):
    #     file = f"{os.getcwd()}{os.sep}shhs1-200002-nsrr.xml"
    #     print(os.path.isfile(file))
    #     with open("shhs1-200002-predictions.npy", "rb") as arr:
    #         predictions = np.load(arr)
    #         self.predictions.predictions = predictions
    #         self.predictions.last_predicted_index = len(predictions)
    #         self.predictions.read_xml_annotations(file)
    #         self.predictions.plot_roc()
    #
    #         print(np.unique(self.predictions.predictions))
    #         print(np.unique(self.predictions.ground_truth))
    #         print(self.predictions.ground_truth[:1000])

    def test_get_predictions_and_ground_truth(self):
        file = f"{os.getcwd()}{os.sep}shhs1-200002-nsrr.xml"
        self.predictions.append_predictions(self.overlap_predictions, 0)
        self.predictions.append_predictions(self.non_overlap_predictions, 2700)

        self.predictions.annotation_file = file
        pred = self.predictions.predictions
        ground_truth = self.predictions.ground_truth
        print(max(pred))
        print(max(ground_truth))
        print(np.unique(pred))
        # pprint.pprint(self.predictions.info)
        print(self.predictions.evaluate.predictionAHI)
        print(self.predictions.evaluate.groundTruthAHI)
        # TODO Write real tests
