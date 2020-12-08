import os


class Config:
    default_weights = "yolov3-416"
    weights_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, "model", default_weights))
    if not os.path.exists(weights_path):
        print(f"Did not find weights at {weights_path}")
