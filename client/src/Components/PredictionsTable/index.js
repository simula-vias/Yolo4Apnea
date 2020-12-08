import React, {useEffect, useState} from "react";
import {Button, Table, Tooltip} from "antd";


function cleanTableRow(row, play, predictionDF, setDisplayEnd, setDisplayStart) {
    let rowDict = predictionDF[row]
    let start = rowDict["start"]
    let end = rowDict["end"]
    let confidence = rowDict["min_confidence"]
    confidence = confidence.toFixed(3)
    let duration = rowDict["duration"]

    let dict = {
        key: row,
        start: start,
        end: end,
        conf: confidence,
        duration: duration,
    }

    if (play) {
        dict["view"] =
            <Tooltip title="Only available when paused">
                <Button disabled>View</Button>

            </Tooltip>
    } else {
        dict["view"] = <Button onClick={() => {
            setDisplayStart(predictionDF[row]["start"] - 200)
            setDisplayEnd(predictionDF[row]["end"] + 200)
        }
        }>View</Button>
    }

    return dict
}

export const PredictionTable = ({predictionDF, setDisplayStart, setDisplayEnd, play}) => {

    const [predictions, setPredictions] = useState()

    const columns = [
        {
            title: 'Start',
            dataIndex: 'start',
            key: 'start',
            width: '18%'
        },
        {
            title: "End",
            dataIndex: "end",
            key: "end",
            width: '18%'
        },
        {
            title: "Minimum Confidence",
            dataIndex: "conf",
            key: "conf",
            width: '24%'
        },
        {
            title: "Duration",
            dataIndex: "duration",
            key: "duration",
            width: '20%'
        },
        {
            title: "View",
            dataIndex: "view",
            key: "view",
            width: '20%'
        }
    ]



    useEffect(() => {
        if (predictionDF) {
            let cleaned_rows = Object.keys(predictionDF).map((row) => {
                return cleanTableRow(row, play, predictionDF, setDisplayEnd, setDisplayStart)
            })
            setPredictions(cleaned_rows)
        }
    }, [predictionDF, play, setDisplayEnd, setDisplayStart])


    return (
        <Table columns={columns} dataSource={predictions}/>
    )
}

