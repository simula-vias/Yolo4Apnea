import React, {useContext, useEffect, useState} from "react";
import SignalContext from "../../utils/SignalContext";
import {Footer} from "../../Components/Footer";
import {PredictionTable} from "../../Components/PredictionsTable";
import {MetricsList} from "../../Components/MetricsList";
import ServerContext from "../../utils/ServerContext";
import {useInterval} from "../../scripts/useinterval";
import {updatePredictions} from "../../scripts/updatePredictions";
import {analyze_recording} from "../../scripts/analyze_recording";
import {DisplaySignal} from "../../Components/Signal/DisplaySignal";
import {PredictedSignal} from "../../Components/Signal/PredictedSignal";
import {Graph} from "../../Components/Graph";
import {updateDisplayState} from "../../scripts/updateDisplayState";

import {getServerStatus} from "../../scripts/serverconnection";
import {Button, Card, Col, Layout, Row} from "antd";


export const DisplayRoute = () => {

    const [id, setID] = useState('_' + Math.random().toString(36).substr(2, 9))

    const {server, setServer} = useContext(ServerContext)
    const {signalObject, setSignalObject} = useContext(SignalContext)

    const abdoSignal = signalObject.abdoSignal
    const slidingWindow = 900

    const [play, setPlay] = useState()
    const [lastViewedIndex, setLastViewedIndex] = useState(0)
    const [displayEnd, setDisplayEnd] = useState(0)
    const [displayStart, setDisplayStart] = useState(0)
    const [predictions, setPredictions] = useState([])
    const [predictionDF, setPredictionDF] = useState()
    const [showAnalyze, setShowAnalyze] = useState()
    const [serverStatus, setServerstatus] = useState(false)
    const [checkServerInterval, setCheckServerInterval] = useState(500)

    useEffect(() => {
        const interval = setInterval(() => {
            updateDisplayState(play, displayEnd, slidingWindow, setDisplayEnd, setLastViewedIndex)
        }, 10) // 100 is default value
        return () => clearInterval(interval)

    }, [play, displayEnd, slidingWindow, setLastViewedIndex])

    useInterval(() => {
        getServerStatus(server)
            .then(status => {
                setServerstatus(status)
                if (status) {
                    setCheckServerInterval(10000)
                }
            })
    }, checkServerInterval)

    return (
        <Layout style={{height: "100vh"}}>
            <Layout.Content>
                <Row justify="center">
                    <Col span={16}>
                        <Row justify="center">
                            <Col span={24}>
                                <Card title="Signal">
                                    <Row justify="center">
                                        <Graph abdoSignal={abdoSignal} displayEnd={displayEnd}
                                               displayStart={displayStart}
                                               predictions={predictions} play={play}>
                                        </Graph>
                                    </Row>
                                    <Row justify="center">
                                        {showAnalyze === undefined &&

                                        <Button type={"primary"} onClick={() => {
                                            setPlay(!play)
                                            setDisplayEnd(lastViewedIndex)
                                            setDisplayStart(0)
                                        }}> {play && "Pause"} {!play && "Play"} </Button>
                                        }

                                        {play === undefined &&
                                        <Button type={"primary"} onClick={() => {
                                            setShowAnalyze(true)
                                            analyze_recording(setPredictions, setDisplayEnd, abdoSignal, updatePredictions, server, id, setPredictionDF)
                                        }}> Analyze </Button>}

                                    </Row>


                                </Card>
                            </Col>
                            <Col span={24}>
                                <Card title={"Predictions"}>
                                    <PredictionTable predictionDF={predictionDF} setDisplayEnd={setDisplayEnd}
                                                     setDisplayStart={setDisplayStart} play={play}>

                                    </PredictionTable>
                                </Card>
                            </Col>
                        </Row>

                    </Col>

                    <Col span={8}>
                        <Card title="Metrics">
                            <MetricsList server={server} id={id} useInterval={useInterval}/>
                        </Card>
                    </Col>
                </Row>
            </Layout.Content>

            <DisplaySignal play={play} displayEnd={displayEnd} setDisplayEnd={setDisplayEnd} displayStart={displayStart}
                           setDisplayStart={setDisplayStart}
                           slidingWindow={slidingWindow}>
            </DisplaySignal>

            <PredictedSignal abdoSignal={abdoSignal} displayEnd={displayEnd} play={play} predictions={predictions}
                             setPredictions={setPredictions} setPredictionDF={setPredictionDF}
                             updatePredictions={updatePredictions}
                             useInterval={useInterval} server={server} id={id}>
            </PredictedSignal>


            <Layout.Footer>
                <Footer server={server} serverStatus={serverStatus} setID={setID}/>
            </Layout.Footer>

        </Layout>


    )
}