import React, {useState} from 'react';


export const ServerConnection = ({apiRoot, useInterval}) => {

    const [serverConnected,setServerConnected] = useState(false)
    const [serverCheckInterval,setServerCheckInterval] = useState(3000)
    useInterval(() => {
            let apiEndpoint = apiRoot + "/serverstatus"

            const requestOptions = {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            }

            fetch(apiEndpoint, requestOptions)
                .then(response => response.json())
                .then((response) => {
                    if (response){
                        setServerConnected(true)
                        setServerCheckInterval(20000)
                    }
                })

    }, serverCheckInterval)

    return <h1> Connected to server?  {serverConnected.toString()}</h1>
}
