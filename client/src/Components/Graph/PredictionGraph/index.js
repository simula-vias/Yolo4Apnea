import React, {useState} from 'react';
import Plot from 'react-plotly.js';

export const PredictionGraph = ({predictions, displayStart, displayEnd, useInterval,signalIndexArray}) => {

    const [graph, setGraph] = useState()

    useInterval(() => {
        setGraph(
            <Plot
                data={[
                    {
                        x: signalIndexArray.slice(displayStart, displayEnd),
                        y: predictions.slice(displayStart, displayEnd),
                        type: "pointcloud",
                        mode: 'lines',
                        showlegend: false,
                        marker: {color: 'red'},
                    }
                ]}
                layout={{width: 1200, height: 300, title: 'Predictions', yaxis: {range: [-0.1, 1]}}}
            />
        )
    }, 500)


    return (
        <>
            {graph}
        </>
    )
}