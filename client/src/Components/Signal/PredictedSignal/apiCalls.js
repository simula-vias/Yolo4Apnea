
export function getPredictionsFromNewSignals(signals,apiRoot,start_index,id) {
    let apiEndpoint = apiRoot + "/predict"
    let requestData = {signal: signals,startIndex: start_index,id:id}

    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    }


    let predictedStartIndex
    let new_predictions

    return fetch(apiEndpoint, requestOptions)
        .then(response => response.json())
        .then((response) => {
            predictedStartIndex = response["start_index"]
            new_predictions = response["last_predictions"]
            return [predictedStartIndex,new_predictions]

        })
}

export function predict_whole_signal(signal,apiRoot,id) {
    console.log("Predicting whole signal!")
    console.log("Signal length:")
    console.log(signal.length)

    let apiEndpoint = apiRoot + "/predict_all"
    let requestData = {signal: signal,id:id}


    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    }

    return fetch(apiEndpoint, requestOptions)
        .then(response => response.json())
        .then((response) => {
            return response["last_predictions"]
        })

}

