export function getPredictionsFromNewSignals(signals,server,start_index,id) {
    let apiEndpoint = server + "/api/predict"
    let requestData = {signal: signals,startIndex: start_index,id:id}

    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    }


    let predictedStartIndex
    let new_predictions

    return fetch(apiEndpoint, requestOptions)
        .then((response) => {
            if (!response.ok) {
                throw Error(response.statusText)
            }
            return response
        })
        .then(response => response.json())
        .then((response) => {
            predictedStartIndex = response["start_index"]
            new_predictions = response["last_predictions"]
            return [predictedStartIndex,new_predictions]
        })
        .catch((error) => {
            throw Error(error)
        })
}