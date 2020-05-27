from src.Recording import Recording
from src.Yolo_predicter import Yolo_predicter
from src.Prediction_analyser import Prediction_analyser

class Prediction:
   
   def __init__(self,patient_path,annotation_path=None,replay=False,demo=False,threshold=0):
      self.patient_path = patient_path
      self.recording = Recording(patient_path,annotation_path=annotation_path,replay=replay)
      self.yolo_predicter = Yolo_predicter(self.recording,replay,demo)


   def report_full(self):
      prediction_file = self.yolo_predicter.prediction_path
      self.prediction_analyser = Prediction_analyser(prediction_file,self.recording)
      report = self.prediction_analyser.get_report_from_multiple_thresholds()
      return report
   
   def get_predictions(self):
      prediction_file = self.yolo_predicter.prediction_path
      self.prediction_analyser = Prediction_analyser(prediction_file,self.recording)
      report = self.prediction_analyser.clean_predictions(0)
      return report