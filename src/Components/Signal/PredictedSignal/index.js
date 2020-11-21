import React, {useEffect, useState} from 'react';
import {getPredictionsFromNewSignals, predictNewSignals} from "../PredictedSignal/apiCalls";



export const PredictedSignal = ({abdoSignal, displayEnd, play, predictions, setPredictions, useInterval,apiRoot,id,}) => {

    const [previousIndex, setPreviousIndex] = useState(0)

    useInterval(() => {
        if (play) {
            getPredictionsFromNewSignals(abdoSignal.slice(previousIndex, displayEnd),apiRoot,previousIndex,id)
                .then((pred) => {
                    let [startIndex,new_predictions] = pred
                    let predictions_tmp = predictions.slice(0,startIndex)
                    predictions_tmp.push(...new_predictions)
                    setPredictions(predictions_tmp)
                    setPreviousIndex(displayEnd)
                })

        }
    }, 4000) //NOTE! Flask server wil run into appending errors if set too short. TODO: Make append_signal or predict() handle these cases


    return (
        <>
            Play is {play.toString()}
        </>
    )
}