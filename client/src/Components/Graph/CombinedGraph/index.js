import React from 'react';
import Plot from "react-plotly.js";

export const CombinedGraph = ({abdoSignal,displayStart,displayEnd,predictions}) => {

        return (
            <>
            <Plot
                data={[
                    {
                        y: abdoSignal !== undefined ? abdoSignal : [],
                        type: "scatter",
                        mode: 'lines',
                        showlegend: false,
                        marker: {color: 'blue'},
                    },
                    {
                        y: predictions !== undefined ? predictions : [],
                        type: "scatter",
                        fill: "tozeroy",
                        mode: 'lines',
                        yaxis: "y2",
                        showlegend: false,
                        line:{
                            width:3
                        },
                        marker: {
                            color: 'red',

                        },
                    }
                ]}
                layout={{
                    height:600,
                    width:1200,
                    title: 'Yolo4Apnea Predictions',
                    yaxis: {
                        range: [-1, 1],
                        title: "Sensor signal",
                        titlefont: {color:"blue"},
                        thickness: 1000

                    },
                    yaxis2: {
                        range: [0,1],
                        side: 'right',
                        title: 'Prediction confidence',
                        titlefont: {color: 'red'},
                        overlaying: 'y',

                    },
                    xaxis: {
                        range: [displayStart,displayEnd],
                        rangeslider: {range:[0,displayEnd]}
                    },
                }}

            />
            </>
        )
}