import React, {useState} from 'react';


export const PredictedSignal = ({abdoSignal, displayEnd, play, predictions, setPredictions, useInterval}) => {

    const [previousIndex, setPreviousIndex] = useState(0)


    useInterval(() => {
        if (play) {
            let new_signals = abdoSignal.slice(previousIndex, displayEnd)

            // API call here
            let apiEndpoint = "http://localhost:5000/api/predict"
            let requestData = {signal: new_signals,startIndex: previousIndex}

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
    }, 1000)


    return (
        <>
            Play is {play.toString()}
        </>
    )
}