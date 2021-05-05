import numpy as np
import os
import yoloapnea.yolo_signal_detector as Yolo
from pathlib import Path
from unittest import TestCase
from yoloapnea.Plotters.pyPlotter import PyPlotter as SignalPlotter


class TestYoloSignalDetector(TestCase):

    def setUp(self):
        test_signal = np.load("shhs1-200753-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]

        self.prediction_duration = 900
        self.prediction_overlap = 450

        size = 416
        conf_thresh = 0.0
        nms_thresh = 0.5

        self.weights_path = str(Path(os.getcwd(), "yolo-obj_last.weights"))
        self.config_path = str(Path(os.getcwd(), "yolo-obj.cfg"))
        self.yolo = Yolo.YoloSignalDetector(self.weights_path, size, conf_thresh, nms_thresh, self.config_path)

        self.signalplotter = SignalPlotter(self.prediction_overlap, self.prediction_overlap)

    def test_detect(self):
        img = self.signalplotter.signal_to_image(self.abdo_signal[89193:89193 + self.prediction_duration])
        predictions = self.yolo.detect(img)
        self.assertGreater(len(predictions), 0)  # NB! This is with current model. May not detect apnea on other models
