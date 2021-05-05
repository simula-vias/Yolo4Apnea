import cv2
import matplotlib.pyplot as plt
import numpy as np

from .signalplotter import SignalPlotter


class PyPlotter(SignalPlotter):

    def __init__(self, image_duration, sliding_window_overlap=None):
        self.image_duration = image_duration
        self.sliding_window_overlap = sliding_window_overlap

    def plot_signal(self, signal):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))

        self.ax.plot(signal)
        self.ax.set_ylim(-1, 1)
        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.ax.grid(False)
        plt.axis('off')

        for i in self.plotting_generator(signal):
            yield i

    def plot_part(self, start, end):
        fig = self.fig
        ax = self.ax
        assert end, start + self.image_duration

        # line = self.ax.plot(self.signal[start:end],'b')
        ax.set_xlim(start, end)
        self.fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # cv2.imshow('image', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        plt.close(fig)
        return img

    def signal_to_image(self, signal, start=0, end=None):
        if end is None:
            end = self.image_duration
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.plot(signal)
        ax.set_ylim(-1, 1)

        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.grid(False)
        plt.axis('off')
        ax.set_xlim(start, end)

        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        plt.close(fig)

        # cv2.imshow('image', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return img
