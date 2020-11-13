import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  # Disables extra info output from tensorflow


class ImageConfig:
    sliding_window_duration = 900
    sliding_window_overlap = 450


class YoloConfig:
    size = 416
    weights = r"C:\Users\Sondre Hamnvik\Documents\INF\Master\data\Weights\yolov3-416"
    iou = 0.45
    score = 0.25
    pred_names = "tensorflow_yolov4/data/classes/coco.names"
    pred_names = os.path.abspath(os.path.join(os.path.dirname(__file__), pred_names))
