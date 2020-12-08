import React, {useEffect, useState} from 'react';
import Plot from "react-plotly.js";

export const Graph = ({abdoSignal,displayStart,displayEnd,predictions,play}) => {

    const [abdoDisplay,setAbdoDisplay] = useState({
        y: abdoSignal !== undefined ? abdoSignal : [],
        type: "scatter",
        mode: 'lines',
        showlegend: false,
        marker: {color: 'blue'},
    })

    const [predictionDisplay,setPredictionDisplay] = useState(
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
    )

    const [layout,setLayout] = useState(
        {
            height: 400,
            width: 800,
            title: 'Yolo4Apnea Predictions',
            yaxis: {
                range: [-1, 1],
                title: "Sensor signal",
                titlefont: {color: "blue"},
                thickness: 1000

            },
            yaxis2: {
                range: [0, 1],
                side: 'right',
                title: 'Prediction confidence',
                titlefont: {color: 'red'},
                overlaying: 'y',

            },
            xaxis: {
                range: [Math.min(displayEnd-900,displayStart),displayEnd],
                rangeslider: {range:[0,displayEnd]}
            },
        }
    )

    //Updates y values for abdo in graph when abdoSignal changes
    useEffect(() => {
        setAbdoDisplay(prevState => {
            return ({...prevState,y: abdoSignal !== undefined ? abdoSignal : []})
        })
    },[abdoSignal])

    //updates y values for predictions when predictions changes
    useEffect(() => {
        setPredictionDisplay(prevState => {
            return ({...prevState,y: predictions !== undefined ? predictions : []})
        })
    },[predictions])

    //Shows range slider if paused, or without if playing
    useEffect(() => {
        setLayout(prevState => {
            if (play || displayEnd === 0) {
                return ({
                    ...prevState, xaxis: {
                        range: [displayEnd - 900, displayEnd],
                    }
                })
            } else {
                return ({
                    ...prevState, xaxis: {
                        range: [Math.max(displayStart, 0), displayEnd],
                        rangeslider: {range: [0, displayEnd]}
                    }
                })
            }
        })
    }, [displayEnd, play, displayStart])


    return (
        <>
            <Plot
                data={[abdoDisplay,predictionDisplay]}
                layout={layout}
            />
        </>
    )
}