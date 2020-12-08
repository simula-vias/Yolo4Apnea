import random
from unittest import TestCase

import numpy as np

import app
from apneapredictor.yoloapnea.config import ImageConfig

sliding_window_duration = ImageConfig.sliding_window_duration


class Test(TestCase):

    def setUp(self):
        print("")
        self.app = app.app
        test_signal = np.load("shhs1-200753-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]

    def test_predict(self):
        with self.app.test_client() as c:
            i = 0
            while i < 3000:
                duration = random.randrange(10, 100)
                signal = list(self.abdo_signal[i:i+duration])

                rv = c.post('/api/predict', json={
                    'signal': signal, 'startIndex': i, "id": "TESTID"
                })
                json_data = rv.get_json()
                if i+duration < sliding_window_duration:
                    self.assertEqual(json_data["start_index"], 0)
                else:
                    self.assertEqual(
                        json_data["start_index"]+sliding_window_duration, i+duration)

                print(
                    f"i: {i} duration: {duration} signal length:{len(signal)} pred length: {len(json_data['last_predictions'])}")
                if i + len(signal) < sliding_window_duration:
                    self.assertEqual(
                        len(json_data["last_predictions"]), i + len(signal))
                else:
                    self.assertEqual(
                        len(json_data["last_predictions"]), sliding_window_duration)

                i += duration
