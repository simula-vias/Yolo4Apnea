export function updatePredictions(server,id,setDF) {

    let apiEndpoint = server + "/api/predictions"
    let requestData = {id: id}

    const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(requestData)
    }

    fetch(apiEndpoint, requestOptions)
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.status)
            } else if (response.status === 204) {
                return {}
            } else {
                return response.json()
            }
        })
        .then(dataframe => {
            if (Object.keys(dataframe).length > 0) {
                setDF(dataframe)
            }
        })
        .catch((error) => {
            console.log(error)
        })
}