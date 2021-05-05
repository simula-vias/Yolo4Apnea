import numpy as np
import pyqtgraph as pg
from yoloapnea.Plotters.signalplotter import SignalPlotter

image_duration = 900
overlap = 450


class PyQtPlotter(SignalPlotter):

    def plot_part(self, start, end):
        print("test from PyQt")
        print(f"start:{start} end:{end}")
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        plt = pg.plot(x, y, pen=None, symbol='o')  ## setting pen=None disables line drawing

        exit()

    def plot_signal(self, signal):
        print("in QT plotter")

        for i in self.plotting_generator(signal):
            yield i
