import React, {useState} from 'react';
import Plot from 'react-plotly.js';


export const SensorGraph = ({abdoSignal, displayStart, displayEnd, useInterval,signalIndexArray}) => {

    const [graph, setGraph] = useState()

    useInterval(() => {
        setGraph(
            <Plot
                data={[
                    {
                        x: signalIndexArray.slice(displayStart, displayEnd),
                        y: abdoSignal.slice(displayStart, displayEnd),
                        type: "pointcloud",
                        mode: 'lines',
                        showlegend: false,
                        marker: {color: 'blue'},
                    }
                ]}
                layout={{width: 1200, height: 500, title: 'Sensor data', yaxis: {range: [-1, 1]}}}
            />
        )
    }, 500)


    return (
        <>
            {graph}
        </>
    )
}