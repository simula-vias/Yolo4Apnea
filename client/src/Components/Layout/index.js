import React, {useEffect, useRef, useState} from 'react';
import {Configuration} from "../Configuration";
import {Graph} from "../Graph";
import {Signal} from "../Signal";


export const Layout = () => {

    const [demoMode, setDemoMode] = useState(false)
    const [abdoSignal, setAbdoSignal] = useState([])
    const [play, setPlay] = useState(false)

    const [displayEnd, setDisplayEnd] = useState(0)
    const [displayStart, setDisplayStart] = useState(0)

    const [predictions, setPredictions] = useState([])

    const slidingWindow = 300

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

            <Graph
                abdoSignal={abdoSignal} displayStart={displayStart} displayEnd={displayEnd}
                slidingWindow={slidingWindow} predictions={predictions} useInterval={useInterval}
            >
            </Graph>

            <Configuration
                demoMode={demoMode} setDemoMode={setDemoMode} play={play} setPlay={setPlay}>
            </Configuration>

            <Signal
                demoMode={demoMode} abdoSignal={abdoSignal} setAbdoSignal={setAbdoSignal} play={play}
                displayEnd={displayEnd} setDisplayEnd={setDisplayEnd} displayStart={displayStart}
                setDisplayStart={setDisplayStart}
                slidingWindow={slidingWindow} predictions={predictions} setPredictions={setPredictions}
                useInterval={useInterval}>
            </Signal>



        </>
    )
}