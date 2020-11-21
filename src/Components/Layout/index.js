import React, {useEffect, useRef, useState} from 'react';
import {Configuration} from "../Configuration";
import {Graph} from "../Graph";
import {Signal} from "../Signal";
import {ServerConnection} from "../ServerConnection";
import {PredictionList} from "../PredictionsList";
import {Grid} from "@material-ui/core";

const id = '_' + Math.random().toString(36).substr(2, 9)

export const Layout = () => {

    const [demoMode, setDemoMode] = useState(false)
    const [abdoSignal, setAbdoSignal] = useState()
    const [play, setPlay] = useState(false)

    const [displayEnd, setDisplayEnd] = useState(0)
    const [displayStart, setDisplayStart] = useState(0)

    const [predictions, setPredictions] = useState([])

    const apiRoot = "http://localhost:5000/api"


    const slidingWindow = 900

    //Copied from https://overreacted.io/making-setinterval-declarative-with-react-hooks/
    function useInterval(callback, delay) {
        const savedCallback = useRef();

        // Remember the latest callback.
        useEffect(() => {
            savedCallback.current = callback;
        }, [callback]);

        // Set up the interval.
        useEffect(() => {
            function tick() {
                savedCallback.current();
            }

            if (delay !== null) {
                let id = setInterval(tick, delay);
                return () => clearInterval(id);
            }
        }, [delay]);
    }

    return (
        <>
            <ServerConnection apiRoot={apiRoot} useInterval={useInterval}>
            </ServerConnection>

            <Grid container>

                <Grid item xs={8}>

                    <Graph
                        abdoSignal={abdoSignal} displayStart={displayStart} displayEnd={displayEnd}
                        slidingWindow={slidingWindow} predictions={predictions} useInterval={useInterval}>

                    </Graph>

                </Grid>

                <Grid item xs={4}>
                    <PredictionList apiRoot={apiRoot} id={id}>
                    </PredictionList>
                </Grid>

            </Grid>


            <Configuration
                demoMode={demoMode} setDemoMode={setDemoMode} play={play} setPlay={setPlay} setAbdoSignal={setAbdoSignal}
                abdoSignal={abdoSignal} apiRoot={apiRoot} id={id} setPredictions={setPredictions}
                setDisplayEnd={setDisplayEnd}>
            </Configuration>

            <Signal
                demoMode={demoMode} abdoSignal={abdoSignal} setAbdoSignal={setAbdoSignal} play={play}
                displayEnd={displayEnd} setDisplayEnd={setDisplayEnd} displayStart={displayStart}
                setDisplayStart={setDisplayStart}
                slidingWindow={slidingWindow} predictions={predictions} setPredictions={setPredictions}
                useInterval={useInterval} apiRoot={apiRoot} id={id}>
            </Signal>


        </>
    )
}