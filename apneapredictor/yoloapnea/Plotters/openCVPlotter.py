import cv2
import numpy as np

from .signalplotter import SignalPlotter

image_duration = 900
overlap = 450


class Plotter:
    def __init__(self, plot_width, plot_height):
        self.width = plot_width
        self.height = plot_height
        self.color = (255, 0, 0)
        self.val = []
        self.plot_canvas = np.ones((self.height, self.width, 3)) * 255

    # Update new values in plot
    def plot(self, val, label="plot"):
        self.val.append(int(val))
        while len(self.val) > self.width:
            self.val.pop(0)

        self.show_plot(label)

    # Show plot using opencv imshow
    def show_plot(self, label):
        self.plot_canvas = np.ones((self.height, self.width, 3)) * 255
        cv2.line(self.plot_canvas, (0, int(self.height / 2)), (self.width, int(self.height / 2)), (0, 255, 0), 1)
        for i in range(len(self.val) - 1):
            cv2.line(self.plot_canvas, (i, int(self.height / 2) - self.val[i]),
                     (i + 1, int(self.height / 2) - self.val[i + 1]), self.color, 1)

        cv2.imshow(label, self.plot_canvas)
        cv2.waitKey(10)


class OpenCVPlotter(SignalPlotter):

    def plot_part(self, start, end):
        print("test from PyQt")
        print(f"start:{start} end:{end}")
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)

        p = Plotter(400, 200)
        for v in range(200):
            p.plot(v)

    def plot_signal(self, signal):
        print("in QT plotter")
        for i in self.plotting_generator(signal):
            yield i
