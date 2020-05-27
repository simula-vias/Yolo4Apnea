import numpy as np
import pandas as pd
from lxml import etree
from pathlib import Path

shhs_interface = False

try:
    import shhs_interface.shhs_interface as shhs_interface
    shhs_interface = True
except ImportError:
    pass

class Annotation_reader:
    def __init__(self,annotation_path):
        self.annotation_path = annotation_path
        self.annotation_has_been_read = False

    @property
    def annotations(self):
        if self.annotation_has_been_read:
            pass
            
        elif self.annotation_path.endswith("xml"):
            self.annotation= self._read_xml()
        else:
            if shhs_interface:
                patient = Path(self.annotation_path).stem
                _,annotations = shhs_interface.get_entry(patient)
                self.annotation = annotations
            else:
                print("Please enter a valid annotation file")
                exit(0)       
        return self.annotation
        
    def _read_xml(self):
        
        events = []

        with open(self.annotation_path) as f:
            tree = etree.parse(f)
            tree = tree.getroot()
            for scored_event in tree.find("ScoredEvents"):
                concept = scored_event.find("EventConcept")
                if concept.text == "Obstructive apnea|Obstructive Apnea":
                    start = np.float(scored_event.find("Start").text)
                    end = start + np.float(scored_event.find("Duration").text)
                    events.append({"START": start*10, "END": end*10})
        df = pd.DataFrame(events)
        return df
