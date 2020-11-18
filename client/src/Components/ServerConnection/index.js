import React, {useState} from 'react';


export const ServerConnection = ({apiRoot, useInterval}) => {

    const [serverConnected,setServerConnected] = useState(false)
    const [serverCheckInterval,setServerCheckInterval] = useState(3000)
    useInterval(() => {
        console.log(!serverConnected)
        if (!serverConnected){
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
        }

    }, serverCheckInterval) //NOTE! Flask server wil run into appending errors if set too short. TODO: Make append_signal or predict() handle these cases

    return <h1> Connected to server?  {serverConnected.toString()}</h1>
}
