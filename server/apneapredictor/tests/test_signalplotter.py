import cv2
import numpy as np
from unittest import TestCase
from yoloapnea.Plotters.pyPlotter import PyPlotter as SignalPlotter

image_duration = 900
overlap = 450


class TestSignalPlotter(TestCase):

    def setUp(self):

        test_signal = np.load("shhs1-200753-signal.npz")
        self.abdo_signal = test_signal["abdo_res"]

        self.plotter = SignalPlotter(image_duration, overlap)

    def test_plot_signal_correct_length(self):
        part_signal = self.abdo_signal[0:image_duration]
        images = self.plotter.plot_signal(part_signal)
        for start_index, img in images:
            shape = img.shape
            self.assertEqual(shape[0], 1000)
            self.assertEqual(shape[1], 1000)
            self.assertEqual(shape[2], 3)

        # cv2.imshow('image', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def test_plot_signal_short_length(self):
        part_signal = self.abdo_signal[0:image_duration - 200]

        with self.assertRaises(Exception):
            for _, img in self.plotter.plot_signal(part_signal):
                pass

    def test_plot_signal_two_images(self):
        part_signal = self.abdo_signal[0:image_duration + overlap]
        images = self.plotter.plot_signal(part_signal)

        image_count = 0

        for _, img in images:
            shape = img.shape
            self.assertEqual(shape[0], 1000)
            self.assertEqual(shape[1], 1000)
            self.assertEqual(shape[2], 3)
            image_count += 1

        self.assertEqual(2, image_count)

    def test_plot_signal_three_images(self):
        part_signal = self.abdo_signal[0:image_duration + overlap + overlap]
        images = self.plotter.plot_signal(part_signal)

        image_count = 0

        for _, img in images:
            shape = img.shape
            self.assertEqual(shape[0], 1000)
            self.assertEqual(shape[1], 1000)
            self.assertEqual(shape[2], 3)
            image_count += 1

        self.assertEqual(3, image_count)

    def test_plot_signal_data_for_one_and_a_half_image(self):
        part_signal = self.abdo_signal[0:image_duration + int((overlap / 2))]

        images = self.plotter.plot_signal(part_signal)

        image_count = 0

        for _, img in images:
            shape = img.shape
            self.assertEqual(shape[0], 1000)
            self.assertEqual(shape[1], 1000)
            self.assertEqual(shape[2], 3)
            image_count += 1

        self.assertEqual(2, image_count)

    def test_plot_signal_data_for_two_and_a_half_image(self):
        part_signal = self.abdo_signal[0:image_duration + overlap + int((overlap / 2))]

        images = self.plotter.plot_signal(part_signal)

        image_count = 0

        for _, img in images:
            shape = img.shape
            self.assertEqual(shape[0], 1000)
            self.assertEqual(shape[1], 1000)
            self.assertEqual(shape[2], 3)
            image_count += 1

        self.assertEqual(3, image_count)

    def test_plot_signal_long_data(self):

        import time
        import statistics

        part_signal = self.abdo_signal[:10000]
        images = self.plotter.plot_signal(part_signal)

        times = []
        start = time.time()
        for _, img in images:
            end = time.time()
            duration = end - start
            times.append(duration)
            start = time.time()

        print(f"Mean time is {statistics.mean(times):.4}")
