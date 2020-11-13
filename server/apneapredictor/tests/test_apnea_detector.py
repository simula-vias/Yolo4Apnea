from unittest import TestCase

import numpy as np
import random
from yoloapnea.apnea_detector import ApneaDetector
from yoloapnea.config import ImageConfig

class TestApneaDetector(TestCase):

    def setUp(self):
        test_signal = np.load("shhs1-200753-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]
        self.thor_signal = test_signal["thor_res"]
        self.sliding_window_duration = ImageConfig.sliding_window_duration
        self.sliding_window_overlap = ImageConfig.sliding_window_overlap

    def test_append_signal_too_little_data(self):
        apnea_predictor = ApneaDetector()
        apnea_predictor.append_signal(self.abdo_signal[0:700])
        predictions = apnea_predictor.predictions.get_predictions_as_np_array()
        self.assertEqual(np.max(predictions[700:]), 0)

    def test_append_signal_many_small_appends(self):
        apnea_predictor = ApneaDetector()

        i = 0
        while i < 100:
            duration = random.randrange(10, 100)
            signal = self.abdo_signal[i:i + duration]
            apnea_predictor.append_signal(signal)
            i += duration

        apnea_predictor.append_signal(self.abdo_signal[0:700])
        predictions = apnea_predictor.predictions.get_predictions_as_np_array()

    def test_append_signal(self):
        apnea_predictor = ApneaDetector()
        apnea_predictor.append_signal(self.abdo_signal[0:900])
        apnea_predictor.append_signal(self.abdo_signal[900:1500])
        true_signal = self.abdo_signal[0:1500]
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(1500, apnea_predictor.signal_length)

    def test_append_signal_long(self):
        apnea_predictor = ApneaDetector()
        apnea_predictor.append_signal(self.abdo_signal[0:900])
        apnea_predictor.append_signal(self.abdo_signal[900:1500])
        apnea_predictor.append_signal(self.abdo_signal[1500:10000])
        true_signal = self.abdo_signal[0:10000]
        appended_signal = apnea_predictor.signal
        np.testing.assert_almost_equal(true_signal, appended_signal, decimal=5)
        self.assertEqual(10000, apnea_predictor.signal_length)

    def test__get_next_unchecked_signal_little_data(self):
        apnea_predictor = ApneaDetector()
        small_index = 30
        medium_index = 50
        start_index = 0

        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:small_index],start_index)
        self.assertEqual(new_index,small_index)
        self.assertEqual(len(prediction),self.sliding_window_duration)

        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:small_index+small_index],start_index+small_index)
        self.assertEqual(new_index,small_index+ small_index)
        self.assertEqual(len(prediction),self.sliding_window_duration)

        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:small_index+small_index+medium_index],start_index+small_index+medium_index)
        self.assertEqual(new_index,small_index+small_index+medium_index)
        self.assertEqual(len(prediction),self.sliding_window_duration)

    def test__get_next_unchecked_signal_not_enough_remaining_data_in_signal(self):
        apnea_predictor = ApneaDetector()
        data_index = 1200
        start_index = 1100

        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:data_index],start_index)
        self.assertEqual(new_index,data_index)
        self.assertEqual(len(prediction),self.sliding_window_duration)
        self.assertListEqual(list(prediction),list(self.abdo_signal[data_index-self.sliding_window_duration:data_index]))


    def test__get_next_unchecked_signal_long_insert(self):
        apnea_predictor = ApneaDetector()
        large_index = 5000
        start_index = 0


        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:large_index],start_index)
        self.assertEqual(new_index,self.sliding_window_overlap)
        self.assertEqual(len(prediction),self.sliding_window_duration)

        start_index = 400
        prediction,new_index,signal_start_index = apnea_predictor._get_next_unchecked_signal(self.abdo_signal[:large_index],start_index)
        self.assertEqual(new_index,self.sliding_window_overlap+start_index)
        self.assertEqual(len(prediction),self.sliding_window_duration)