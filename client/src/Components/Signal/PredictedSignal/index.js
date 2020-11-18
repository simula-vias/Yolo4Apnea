import React, {useState} from 'react';

const id = '_' + Math.random().toString(36).substr(2, 9)


export const PredictedSignal = ({abdoSignal, displayEnd, play, predictions, setPredictions, useInterval,apiRoot}) => {

    const [previousIndex, setPreviousIndex] = useState(0)

    useInterval(() => {
        if (play) {
            let new_signals = abdoSignal.slice(previousIndex, displayEnd)

            let apiEndpoint = apiRoot + "/predict"
            let requestData = {signal: new_signals,startIndex: previousIndex,id:id}

            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            }

            fetch(apiEndpoint, requestOptions)
                .then(response => response.json())
                .then((response) => {
                    let predictedStartIndex = response["start_index"]
                    let new_predictions = response["last_predictions"]
                    let predictions_tmp = predictions.slice(0,predictedStartIndex)
                    predictions_tmp.push(...new_predictions)
                    setPredictions(predictions_tmp)
                })
            setPreviousIndex(displayEnd)
        }
    }, 4000) //NOTE! Flask server wil run into appending errors if set too short. TODO: Make append_signal or predict() handle these cases


    return (
        <>
            Play is {play.toString()}
        </>
    )
}