import React, {useContext, useState} from "react";
import ServerContext from "../../utils/ServerContext";
import {getServerStatus} from "../../scripts/serverconnection";
import {useInterval} from "../../scripts/useinterval";
import {setNewEdfFile} from "../../scripts/setNewEDFfile";
import SignalContext from "../../utils/SignalContext";
import {useHistory} from "react-router-dom";
import demo_abdo from "../../res/demo_abdo.json"
import "./style.css"
import {Button, Card, Col, Layout, List, Modal, Row, Upload} from "antd";
import {CheckCircle, Error} from "@material-ui/icons";


export const MainRoute = () => {

    const {server, setServer} = useContext(ServerContext)
    const {signalObject, setSignalObject} = useContext(SignalContext)
    const [serverStatus, setServerstatus] = useState(false)
    const [modalOpen, setModalOpen] = useState(false)

    const [checkServerInterval, setCheckServerInterval] = useState(500)


    let history = useHistory()

    useInterval(() => {
        getServerStatus(server)
            .then(status => {
                setServerstatus(status)
                if (status) {
                    setCheckServerInterval(10000)
                }
            })
    }, checkServerInterval)

    function setAbdoSignal(signal, sensor) {
        let objectCopy = {...signalObject};
        objectCopy.abdoSignal = signal;
        objectCopy.sensor = sensor
        setSignalObject(objectCopy);
    }


    return (
        <Layout style={{height: "100vh"}}>
            <Layout.Content>
                <Row justify="center" style={{paddingTop: "100px"}}>
                    <Card title="Yolo4Apnea">

                        <List
                            size="large"
                            bordered
                            header={<b>Select Yolo4Apnea server</b>}
                        >
                            <List.Item>
                                Server: {server}

                            </List.Item>
                            <List.Item>
                                Status:
                                {serverStatus && <> ok <CheckCircle style={{fill: "green"}}>Connected</CheckCircle> </>}
                                {!serverStatus && <> Waiting to connect <Error style={{fill: "orange"}}> </Error> </>}
                            </List.Item>

                        </List>

                        <Col>
                            <Button type="primary" className={"block-button"} onClick={() => setModalOpen(true)}>
                                Get Started
                            </Button>
                        </Col>


                        <Modal
                            title="Select signal input"
                            centered
                            visible={modalOpen}
                            onOk={() => setModalOpen(false)}
                            onCancel={() => setModalOpen(false)}
                        >

                            <Row justify="space-around">

                                <Col span={7}>
                                    <Button type="primary" className={"tall-button"}>Connect to sensor (Not
                                        implemented)</Button>

                                </Col>

                                <Col span={7}>
                                    <Upload
                                        beforeUpload={event => {
                                            const reader = new FileReader();
                                            reader.onload = e => {
                                                setNewEdfFile(e, setAbdoSignal)
                                                history.push("/display")
                                            };
                                            reader.readAsArrayBuffer(event)
                                            return false
                                        }}>

                                        <Button type="primary" className={"tall-button"}>Upload File</Button>
                                    </Upload>
                                </Col>

                                <Col span={7}>
                                    <Button type="primary" className={"tall-button"}
                                            onClick={() => {
                                                setAbdoSignal(demo_abdo, "DEMO")
                                                history.push("/display")
                                            }}
                                    >Demo</Button>

                                </Col>

                            </Row>

                        </Modal>
                    </Card>

                </Row>
            </Layout.Content>

        </Layout>


    )
}
