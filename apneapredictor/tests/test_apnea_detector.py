import numpy as np
import os
import random
from pathlib import Path
from unittest import TestCase
from yoloapnea.apnea_detector import ApneaDetector
from yoloapnea.apneas import ApneaType


class TestApneaDetector(TestCase):

    def setUp(self):
        test_signal = np.load("shhs1-200703-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]
        self.thor_signal = test_signal["thor_res"]
        self.sliding_window_duration = 900
        self.sliding_window_overlap = 450

        self.apnea_types = ["Obstructive"]

        self.size = 416
        self.conf_thresh = 0.0
        self.nms_thresh = 0.5

        self.plotter = "PyPlot"

        self.weights_path = str(Path(os.getcwd(), "yolo-obj_last.weights"))
        self.config_path = str(Path(os.getcwd(), "yolo-obj.cfg"))
        self.apnea_predictor = ApneaDetector(self.weights_path, self.config_path, self.apnea_types,
                                             self.sliding_window_duration, self.sliding_window_overlap, self.size,
                                             self.conf_thresh, self.nms_thresh, self.plotter)

    def test_append_signal_too_little_data(self):
        apnea_predictor = self.apnea_predictor

        apnea_predictor.append_signal(self.abdo_signal[0:700])
        predictions = self.apnea_predictor.predictions.predictions
        np.testing.assert_almost_equal(self.abdo_signal[0:700], apnea_predictor.signal, decimal=5)

    def test_append_signal_many_small_appends(self):
        apnea_predictor = self.apnea_predictor

        i = 0
        while i < 100:
            duration = random.randrange(10, 100)
            signal = self.abdo_signal[i:i + duration]
            apnea_predictor.append_signal(signal)
            i += duration

        apnea_predictor.append_signal(self.abdo_signal[0:700])
        predictions = apnea_predictor.predictions.predictions

    def test_append_long_signal(self):
        apnea_predictor = self.apnea_predictor
        apnea_predictor.append_signal(self.abdo_signal[0:10000])
        true_signal = self.abdo_signal[0:10000]
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(10000, apnea_predictor.signal_length)

    def test_append_signal(self):
        apnea_predictor = self.apnea_predictor
        apnea_predictor.append_signal(self.abdo_signal[0:900])
        apnea_predictor.append_signal(self.abdo_signal[900:1500])
        true_signal = self.abdo_signal[0:1500]
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(1500, apnea_predictor.signal_length)

    def test_append_signal_long(self):
        apnea_predictor = self.apnea_predictor
        apnea_predictor.append_signal(self.abdo_signal[0:900])
        apnea_predictor.append_signal(self.abdo_signal[900:1500])
        apnea_predictor.append_signal(self.abdo_signal[1500:10000])
        true_signal = self.abdo_signal[0:10000]
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(10000, apnea_predictor.signal_length)

    def test_append_signal_multiple_detectors(self):
        apnea_predictor_1 = self.apnea_predictor
        apnea_predictor_2 = ApneaDetector(self.weights_path, self.config_path, self.apnea_types,
                                          self.sliding_window_duration, self.sliding_window_overlap, self.size,
                                          self.conf_thresh, self.nms_thresh, self.plotter)
        apnea_predictor_1.append_signal(self.abdo_signal[0:900])
        apnea_predictor_1.append_signal(self.abdo_signal[900:1500])

        apnea_predictor_2.append_signal(self.abdo_signal[0:900])
        apnea_predictor_2.append_signal(self.abdo_signal[900:1500])
        apnea_predictor_2.append_signal(self.abdo_signal[1500:10000])

        self.assertEqual(apnea_predictor_1.signal_length, 1500)
        self.assertEqual(apnea_predictor_2.signal_length, 10000)
        self.assertNotEqual(apnea_predictor_1.signal_length, apnea_predictor_2.signal_length)

    def test_append_signal_analyze_whole_recording(self):
        apnea_predictor = self.apnea_predictor
        apnea_predictor.append_signal(self.abdo_signal)
        true_signal = self.abdo_signal
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(len(true_signal), apnea_predictor.signal_length)
        df = apnea_predictor.predictions.evaluate.get_predictions_as_df(apnea_predictor.predictions.predictions)
        print(df)
        ahi = apnea_predictor.predictions.evaluate.predictionAHI
        print(ahi)

    def test_save_prediction_array(self):
        apnea_predictor = self.apnea_predictor
        test_signal = np.load("shhs1-200002-signal.npz")["abdo_res"]
        print(test_signal)
        apnea_predictor.append_signal(test_signal)

        with open("shhs1-200002-predictions.npy", "wb") as f:
            np.save(f, apnea_predictor.predictions.predictions[:apnea_predictor.predictions.last_predicted_index])
