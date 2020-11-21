import React from 'react';
import {Demo} from "./Demo";
import {DisplaySignal} from "./DisplaySignal";
import {PredictedSignal} from "./PredictedSignal";


export const Signal = ({demoMode, abdoSignal, setAbdoSignal, play, displayEnd, setDisplayEnd, displayStart, setDisplayStart,
                           slidingWindow, predictions, setPredictions, useInterval, apiRoot,id}) => {


    return (
        <>

            {demoMode && <Demo setAbdoSignal={setAbdoSignal}>

            </Demo>}

            <DisplaySignal play={play} displayEnd={displayEnd} setDisplayEnd={setDisplayEnd} displayStart={displayStart}
                           setDisplayStart={setDisplayStart}
                           slidingWindow={slidingWindow}>

            </DisplaySignal>

            <PredictedSignal abdoSignal={abdoSignal} displayEnd={displayEnd} play={play} predictions={predictions}
                             setPredictions={setPredictions}
                             useInterval={useInterval}
                             apiRoot={apiRoot} id={id}>

            </PredictedSignal>


            Abdo signal is of length {abdoSignal !== undefined ? abdoSignal.length : 0}

        </>
    )
}