import logging
from flask_cors import CORS

import numpy as np
import sys

from flask import Flask, request, jsonify
import apneapredictor.yoloapnea as yoloapnea

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
            clients[id] = yoloapnea.ApneaDetector()

        detector = clients[id]

        print(clients, file=sys.stderr)

        detector.append_signal(signal)
        predictions,start_index = detector.predictions.get_last_predictions()

        last_predictions = {"start_index": start_index,
                               "last_predictions": list(predictions)}

        print(last_predictions)
        jsonified_predictions = jsonify(last_predictions)
        return jsonified_predictions

@app.route("/api/serverstatus")
def serverstatus():
    print("SERVERSTATUS")
    jsonified_predictions = jsonify(True)
    print(jsonified_predictions)
    return jsonified_predictions

if __name__ == '__main__':
    app.run()
