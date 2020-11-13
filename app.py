import logging
from flask_cors import CORS

import numpy as np


from flask import Flask, request, jsonify
import apneapredictor.yoloapnea as yoloapnea

app = Flask(__name__)
detector = yoloapnea.ApneaDetector()

@app.route("/api/predict",methods=['POST'])
def predict():
    print("running predict")

    if request.method=='POST':

        data = request.get_json()
        signal = data["signal"]
        signal = np.asarray(signal)
        detector.append_signal(signal)

        predictions,start_index = detector.predictions.get_last_predictions()

        last_predictions = {"start_index": start_index,
                               "last_predictions": list(predictions)}

        print("predictions")
        print(last_predictions)

        jsonified_predictions = jsonify(last_predictions)
        return jsonified_predictions

if __name__ == '__main__':
    app.run()
