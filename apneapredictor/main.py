import argparse
import os
from yoloapnea.apnea_detector import ApneaDetector
import pandas as pd
import numpy as np
import pyedflib

class CLI:
    def __init__(self,signal_file=None,signal_type="ABDO_RES"):
        signal_file = os.getcwd() + os.sep + signal_file
        self.edf_signal = self.readEdfFile(signal_file)
        self.signal = self.edf_signal[signal_type].to_numpy()

        self.apnea_detector = ApneaDetector()
        self.apnea_detector.append_signal(self.signal)
        predictions = self.apnea_detector.predictions
        xml = predictions.get_xml()
        print(xml)
        print(predictions.get_predictions_as_np_array())

    def readEdfFile(self,file):
        """Reads EDF file from SHHS dataset. Will need adjustments to work for other signals
        Arguments:
            file {str} -- Path to edf file

        Returns:
            DataFrame -- Dataframe of thorax and abdominal signals, with index in deciseconds since start of recording
        """
        try:
            edf = pyedflib.EdfReader(file)
            cols = edf.getSignalLabels()

            signal = pd.DataFrame([])
            signal['THOR_RES'] = edf.readSignal(cols.index("THOR RES"))
            signal['ABDO_RES'] = edf.readSignal(cols.index("ABDO RES"))
            signal['SUM'] = signal['ABDO_RES'] + signal['THOR_RES']

        finally:
            edf._close()
            del edf

        return signal



if __name__ == '__main__':
    print("Starting cli")
    parser = argparse.ArgumentParser(description='Predict Apnea events on .edf file ',
                                     prog="main.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='path to a .edf file to analyze')
    args = parser.parse_args()
    cli = CLI(signal_file=args.file)


