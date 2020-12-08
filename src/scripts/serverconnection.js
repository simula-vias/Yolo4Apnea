export function getServerStatus(serverAddress){
    let apiEndpoint = serverAddress + "/api/serverstatus"
    const requestOptions = {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    }

    return fetch(apiEndpoint, requestOptions)
        .then(response => response.json())
        .then((response) => {
            if (response){
                return true
            }
        })
        .catch(error => {
            return false
        })

}