import os


class Config:
    default_weights = "yolov3-416"
    weights_path = os.path.join("..", "..", "model", "yolov4_apnea_last.weights")

    if not os.path.exists(weights_path):
        print(f"Did not find weights at {weights_path}")

    cfg_path = os.path.join("..", "..", "model", "yolov4_apnea.cfg")

    if not os.path.exists(cfg_path):
        print(f"Did not find config at {cfg_path}")

    sliding_window_duration = 1200
