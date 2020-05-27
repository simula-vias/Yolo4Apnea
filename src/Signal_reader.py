import os
import pyedflib
import pandas as pd
import numpy as np
from src.config import tmp_dir, tmp_signal_name
from pathlib import Path
import shhs_interface.shhs_interface as shhs_interface

class Signal_reader:
    def __init__(self,patient_path,replay):
        if not replay:
            self.patient_path = patient_path
        else:
            self.patient_path = f"{tmp_dir}{tmp_signal_name}"
        self.signal_has_been_read = False
        self.signal
        
    @property
    def signal(self):
        if self.signal_has_been_read:
            pass
        
        elif self.patient_path.endswith(".edf"):
            self.signal_df = self._read_edf()
            self.signal_has_been_read = True
            
        elif self.patient_path.endswith(".npz"):
            self.signal_df = np.load(self.patient_path)
            signal = {}
            signal["THOR_RES"] = self.signal_df["thor_res"]
            signal["ABDO_RES"] = self.signal_df["abdo_res"]
            self.signal_df = pd.DataFrame(signal)
            self.signal_has_been_read = True
            
        else:
            patient = Path(self.patient_path).stem
            signal,_ = shhs_interface.get_entry(patient)
            print(signal)
            self.signal_df = signal    
            print(patient)
            print(self.signal_df)
            self.signal_has_been_read = True
        
        return self.signal_df
            
    def _read_edf(self):
        try:
            edf = pyedflib.EdfReader(self.patient_path)
            cols = edf.getSignalLabels()

            signal = pd.DataFrame([])
            signal['THOR_RES'] = edf.readSignal(cols.index("THOR RES"))
            signal['ABDO_RES'] = edf.readSignal(cols.index("ABDO RES"))
            signal['SUM'] = signal['ABDO_RES'] + signal['THOR_RES']

        finally:
            edf._close()
            del edf
        self.signal_length = len(signal)
        return signal
    
    def save_signal_to_tmp(self):
        print(self.signal)
        np.savez_compressed(f"{tmp_dir}{tmp_signal_name}",
                            thor_res=self.signal.THOR_RES,abdo_res=self.signal.ABDO_RES)
    
    @property
    def length(self):
        if self.signal_has_been_read:
            return len(self.signal)
        else:
            assert(False)