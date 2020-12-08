export function getMetrics(server, id) {
    let apiEndpoint = server + "/api/prediction_metrics"
    let requestData = {id: id}

    const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(requestData)
    }
    return fetch(apiEndpoint, requestOptions)
        .then((response) => {
            if (!response.ok) {
                throw Error(response.statusText)
            }
            return response
        })
        .then((response) => {
            return response.json()
        })
        .then((response) => {
            return response
        })
        .catch((error) => {
            console.log("No prediction metrics recieved")
        })

}