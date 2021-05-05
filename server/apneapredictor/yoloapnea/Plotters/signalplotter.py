import cv2
import matplotlib.pyplot as plt
import numpy as np


class SignalPlotter:

    def __init__(self, image_duration, sliding_window_overlap=None):
        self.image_duration = image_duration
        self.sliding_window_overlap = sliding_window_overlap

    def plotting_generator(self, signal):
        remaining_signal = len(signal)
        start_index = 0

        if remaining_signal < self.image_duration:
            raise Exception("Signal length is too short")

        if self.sliding_window_overlap is None:
            raise Exception("Add sliding window overlap if plotting multiple images")

        while remaining_signal > 0:

            if remaining_signal <= self.image_duration:
                if remaining_signal < self.image_duration:
                    start_index = len(signal) - self.image_duration

                yield start_index, self.plot_part(len(signal) - remaining_signal, len(signal))
                remaining_signal = 0

            elif remaining_signal > self.image_duration:
                yield start_index, self.plot_part(len(signal) - remaining_signal,
                                                  len(signal) - remaining_signal + self.image_duration)

                # yield start_index,self.signal_to_image(signal[start_index:start_index + self.image_duration])
                start_index = start_index + self.sliding_window_overlap
                remaining_signal -= self.sliding_window_overlap

            else:
                raise Exception("Unhandled else branch")
