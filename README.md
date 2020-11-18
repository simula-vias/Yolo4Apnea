# Yolo4Apnea


# Description
Server-client infrastructure to run real-time detection of apneas using YOLO as 
talken about in the Yolo4Apnea: Real-time Detection of Obstructive Sleep Apnea
demo paper.

##  Note:  Project is not finished, and will be upgraded incrementally

# Requirements
- python3
- npm

## Usage:



### Start Server:
cd to server directory and run:

```bash
pip install -r requirements.txt
python app.py
```
### Start Client:
cd to client directory and run:

Instantiate:
```bash
npm install
npm start
```

## View predictions

- Press the demo button in the web browser window opened by npm.
- Press play
- See the simulated signal appear in the top graph, and the prediction confidence in the lower graph. The lower graph is expected to stay at 0 most of the time, until an apnea is detected
