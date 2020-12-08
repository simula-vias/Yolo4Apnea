from unittest import TestCase

import numpy as np

import yoloapnea.yolo_signal_detector as Yolo
from yoloapnea.config import ImageConfig, YoloConfig


class TestYoloSignalDetector(TestCase):

    def setUp(self):
        test_signal = np.load("shhs1-200753-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]

        self.prediction_duration = ImageConfig.sliding_window_duration
        self.yolo = Yolo.YoloSignalDetector(
            YoloConfig.weights,
            YoloConfig.size,
            YoloConfig.iou,
            YoloConfig.score)

    def test_detect(self):
        predictions = self.yolo.detect(
            self.abdo_signal[89193:89193 + self.prediction_duration])
        # NB! This is with current model. May not detect apnea on other models
        self.assertGreater(len(predictions), 0)
