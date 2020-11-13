import React, {useEffect, useState} from 'react';
import {SensorGraph} from "./SensorGraph";
import {PredictionGraph} from "./PredictionGraph";
import Grid from "@material-ui/core/Grid";

export const Graph = ({abdoSignal, displayStart, displayEnd, predictions, useInterval}) => {

    const [signalIndexArray, setSignalIndexArray] = useState([])


    useEffect(() => {
        let arrayIndex = Array.from(Array(abdoSignal.length).keys())
        setSignalIndexArray(arrayIndex)
    }, [abdoSignal])


    return (

        <>
            <Grid container direction="column" alignItems={"center"} justify={"center"}>
                <Grid item xs={12}>
                    <SensorGraph abdoSignal={abdoSignal} displayEnd={displayEnd} displayStart={displayStart} signalIndexArray={signalIndexArray} useInterval={useInterval}>
                    </SensorGraph>
                </Grid>

            <Grid xs={12}>
                <PredictionGraph predictions={predictions} displayEnd={displayEnd}
                                 displayStart={displayStart} signalIndexArray={signalIndexArray} useInterval={useInterval}>
                </PredictionGraph>
            </Grid>

            </Grid>
        </>
    )
}