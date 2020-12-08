import React, {useState} from "react";

import {getMetrics} from "../../scripts/getMetrics";
import {Table} from "antd";


export const MetricsList = ({server, id, useInterval}) => {

    const [metrics, setMetrics] = useState([])

    const columns = [
        {
            title: 'Metric',
            dataIndex: 'metric',
            key: 'metric',
        },
        {
            title: "Value",
            dataIndex: "value",
            key: "value",
        }
    ]


    function cleanTableRow(metrics, row) {
        let val = metrics[row]
        val = val.toFixed(2)

        let metric = row
        return {
            key: metric,
            value: val,
            metric: metric
        }
    }

    useInterval(() => {
        getMetrics(server, id, setMetrics)
            .then(metrics => {
                if (metrics !== undefined) {
                    let cleaned_rows = Object.keys(metrics["prediction"]).map((row) => {
                        return cleanTableRow(metrics["prediction"], row)
                    })
                    setMetrics(cleaned_rows)
                }

            })
    }, 5000)


    return (
        <Table columns={columns} dataSource={metrics}/>
    )
}