import React, {useEffect, useState} from 'react';
import Grid from "@material-ui/core/Grid";
import {CombinedGraph} from "./CombinedGraph";

export const Graph = ({abdoSignal, displayStart, displayEnd, predictions, useInterval}) => {

    const [signalIndexArray, setSignalIndexArray] = useState([])


    useEffect(() => {
        if( abdoSignal !== undefined){
            let arrayIndex = Array.from(Array(abdoSignal.length).keys())
            setSignalIndexArray(arrayIndex)
        }
    }, [abdoSignal])


    return (

        <>
            <Grid container direction="column" alignItems={"center"} justify={"center"}>
                <Grid item xs={12}>
                    <CombinedGraph abdoSignal={abdoSignal} displayEnd={displayEnd} displayStart={displayStart}
                                 signalIndexArray={signalIndexArray} useInterval={useInterval} predictions={predictions}>
                    </CombinedGraph>
                </Grid>
            </Grid>
        </>
    )
}