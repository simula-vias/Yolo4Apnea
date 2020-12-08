export function predictWholeSignal(signal,apiRoot,id) {
    console.log("Predicting whole signal of length: "+signal.length)

    let apiEndpoint = apiRoot + "/api/predict_all"
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
