# Yolo_Apnea_Predicter

### NB! Still a work in progress, expect interface to change


Master thesis code for predicting apnea events using yolo.
Predict Apnea events on ABDO signal from .edf file or other numpy array signal using trainled Yolo model.
Outputs nsrr-xml info, but wil later be expanded to be able to compare to true signals annotated by sleep technicians,
and will return values of how good the predictions are.

When more models have been generated and trained, the intention is that this repo will handle them as well by changing
paramenters when initializing the detector



# Description
Predict Apnea events on .edf file or ABDO_RES signal and returns an predictions object with 
different ways to visualize the predictions.

This package can be run as a [standalone](#Standalone-from-main) detector, or can be [imported in other projects](#Imported-in-other-projects)


# Imported in other projects

## Usage:

### Run yolo on signal:
Import as:
```python
from yoloapnea.apnea_detector import ApneaDetector
```

Instantiate:
```python
detector = ApneaDetector()
```

Run yolo on signal:

```python
signal = np.array of shape (x,) # Currently needs to be ABDO_RES signal
detector.append_signal(signal)
```

### Access predictions
Needs to be done after the previous part to have generated predictions.

Get prediction object:

```python
predictions = detector.predictions
```

Get NSRR xml output of predictions:

```python
xml = predictions.get_xml()
```

Get numpy array of predictions

```python
xml = predictions.get_predictions_as_np_array()
```

Get numpy array of the most recent predictions 
Usefull for real-time detection.
Returns an array of the same length as the sliding window durtation
```python
xml = predictions.get_last_predictions()
```

---
# Standalone from main
## Usage:


```bash
usage: main.py [-h] file
```
## Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
