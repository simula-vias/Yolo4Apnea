import {useState} from 'react';
import {getPredictionsFromNewSignals} from "../../../scripts/getPredictionsFromNewSignals";

export const PredictedSignal = ({abdoSignal, displayEnd, play, predictions, setPredictions, useInterval,server,id,updatePredictions,setPredictionDF}) => {

    const [previousIndex, setPreviousIndex] = useState(0)

    useInterval(() => {
        if (play) {
            getPredictionsFromNewSignals(abdoSignal.slice(previousIndex, displayEnd),server,previousIndex,id)
                .then((pred) => {
                    let [startIndex,new_predictions] = pred
                    let predictions_tmp = predictions.slice(0,startIndex)
                    predictions_tmp.push(...new_predictions)
                    setPredictions(predictions_tmp)
                    setPreviousIndex(displayEnd)
                    return new_predictions
                })
                .then((pred) => {
                    if (pred.every((x) => x === 0)){
                        updatePredictions(server,id,setPredictionDF)
                    }
                })
                .catch((error) => {
                    console.log(error)
                })

        }
    }, 1000) //NOTE! Flask server wil run into appending errors if set too short. TODO: Make append_signal or predict() handle these cases


    return (null)
}