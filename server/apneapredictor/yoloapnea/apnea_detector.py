import cv2
import numpy as np
import progressbar

from .Plotters.pyPlotter import PyPlotter as SignalPlotter
from .apneas import ApneaType
from .predictions import Predictions
from .yolo_signal_detector import YoloSignalDetector


class ApneaDetector:

    def __init__(self, weights_path, config_path, apnea_types_list, sliding_window_duration, sliding_window_overlap,
                 yolosize, conf_thresh, nms_thresh, plotter):
        self.sliding_window_duration = sliding_window_duration
        self.sliding_window_overlap = sliding_window_overlap

        self.signal_index = 0
        self.signal_length = 0
        self.signal = np.zeros(15 * 60 * 60 * 10)

        self.weights = weights_path
        self.config = config_path

        apnea_types = [ApneaType[a] for a in apnea_types_list]

        self.predictions = Predictions(self.sliding_window_duration, apnea_types, 0.25)
        if plotter == "PyPlot":
            from .Plotters.pyPlotter import PyPlotter as Plotter
            self.signalPlotter = Plotter(self.sliding_window_duration, self.sliding_window_overlap)
        else:
            raise NotImplementedError("Plotter type not implemented")

        size = yolosize
        conf_thresh = conf_thresh
        nms_thresh = nms_thresh

        self.yolo = YoloSignalDetector(self.weights, size, conf_thresh, nms_thresh, self.config)

    def append_signal(self, signal):
        """
        Appends newly received sensor data to the data already stored. Runs yolo on signal to detect apnea.

        :param signal: np array of new signal

        :return: None. Predictions can be accessed from predictions object (self.predictions).
        """

        self._signal[self.signal_length:self.signal_length + len(signal)] = signal
        self.signal_length += len(signal)

        progressbar_value = self.sliding_window_duration if len(signal) < self.sliding_window_duration else len(signal)
        progress = progressbar.ProgressBar(max_value=progressbar_value)
        progress.update(self.signal_index)
        self._predict_unchecked_data(progress)

    @property
    def signal(self):
        return self._signal[:self.signal_length]

    @signal.setter
    def signal(self, signal):
        self._signal = signal

    def _predict_unchecked_data(self, progress):
        """
        Iterates through the data that has not been analyzed by yolo yet.
        Appends np array of 0's if there is to little data, otherwise recursively predicts apneas
        on the remaining data with a stride of {self.sliding_window_overlap}.

        If newly added data is less than {self.sliding_window_overlap} it predicts all the new data
        and whatever is needed before to reach {self.sliding_window_duration}
        """

        signal_start_index_with_guaranteed_overlap = self.signal_index - self.sliding_window_overlap
        signal_start_index_with_guaranteed_overlap = 0 if signal_start_index_with_guaranteed_overlap < 0 else signal_start_index_with_guaranteed_overlap

        signal_to_plot = self.signal[signal_start_index_with_guaranteed_overlap:self.signal_length]
        added_before_start = 0

        if self.signal_length < self.sliding_window_duration:
            zeroedArray = np.zeros(self.sliding_window_duration)
            zeroedArray[-len(signal_to_plot):] = signal_to_plot
            added_before_start = len(signal_to_plot) - self.sliding_window_duration
            signal_to_plot = zeroedArray

        elif len(signal_to_plot) < self.sliding_window_duration:
            added_before_start = self.sliding_window_duration - len(signal_to_plot)
            signal_to_plot = self.signal[-self.sliding_window_duration:]

        images = self.signalPlotter.plot_signal(signal_to_plot)

        for index, img in images:
            true_index = index + added_before_start
            self._predict_image(img, true_index)
            progress_index = true_index + self.sliding_window_duration - self.signal_index
            progress_index = 0 if progress_index < 0 else progress_index
            progress.update(progress_index)

        self.signal_index = self.signal_length

    def _predict_image(self, img, start_index):
        """
        Local helper function for running yolo on a signal of already correct length and inserts the predictions
        into the prediction object

        :param signal: signal to detect: Should always be {self.sliding_window_duration} length
        :param start_index: index of signal[0] in {self.signal} for knowing when predictions start
                since start of recording
        """
        detections = self.yolo.detect(img, show_bbox=False)
        self.predictions.append_predictions(detections, start_index)
