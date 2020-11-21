import logging
from flask_cors import CORS

import numpy as np
import sys
import pandas as pd

from flask import Flask, request, jsonify
import apneapredictor.yoloapnea as yoloapnea
from config import Config

app = Flask(__name__)
CORS(app)


print("initalising detector")
print("This may take some time")
yoloapnea.ApneaDetector()
print("Initialisation done")

example_prediction = np.zeros(100)
example_prediction[50:] = 1
example_index = 0


clients = {}

@app.route("/api/predict",methods=['POST'])
def predict():
    if request.method=='POST':

        data = request.get_json()
        signal = data["signal"]
        signal = np.asarray(signal)

        id = data["id"]

        if id not in clients:
            weights_path = Config.weights_path
            clients[id] = yoloapnea.ApneaDetector(weights_path=weights_path)

        detector = clients[id]

        print("new signal recieved:")
        print(signal)
        detector.append_signal(signal)
        predictions,start_index = detector.predictions.get_last_predictions()

        last_predictions = {"start_index": start_index,
                               "last_predictions": list(predictions)}

        jsonified_predictions = jsonify(last_predictions)
        return jsonified_predictions

@app.route("/api/serverstatus")
def serverstatus():
    jsonified_predictions = jsonify(True)
    return jsonified_predictions


@app.route("/api/predictions",methods=['POST'])
def predictions():
    if request.method == 'POST':
        data = request.get_json()
        id = data["id"]

        if id not in clients:
            return jsonify({}), 204
        else:
            detector = clients[id]
    df = detector.predictions.get_predictions_as_df()
    print(df)
    jsonified_predictions = df.to_json(orient="index")
    return jsonified_predictions


@app.route("/api/predict_all",methods=['POST'])
def predict_all():
    if request.method=='POST':

        data = request.get_json()
        signal = data["signal"]
        signal = np.asarray(signal)

        id = data["id"]
        weights_path = Config.weights_path
        detector = yoloapnea.ApneaDetector(weights_path=weights_path)
        clients[id] = detector

        detector.append_signal(signal)
        predictions = detector.predictions.get_predictions_as_np_array()[:len(detector.signal)]

        last_predictions = {"last_predictions": list(predictions)}

        jsonified_predictions = jsonify(last_predictions)
        return jsonified_predictions


if __name__ == '__main__':
    app.run()
