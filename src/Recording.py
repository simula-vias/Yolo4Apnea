from src.Signal_reader import Signal_reader
from src.Annotation_reader import Annotation_reader
from pathlib import Path


class Recording:
    def __init__(self,patient_path,annotation_path=None,replay=False):

        
        self.signal = Signal_reader(patient_path,replay)
        self.patient = Path(patient_path).stem
        self.annotation = Annotation_reader(annotation_path)
        
    @property
    def length(self):
        return self.signal.length