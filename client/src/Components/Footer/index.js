import React from 'react';
import {useHistory} from "react-router-dom";
import "./style.css"
import {CheckCircle, Error} from "@material-ui/icons";
import {Button, Col, Row} from "antd";

export const Footer = ({server, serverStatus, setID}) => {

    let history = useHistory()

    return (

        <Row justify={"center"}>
            <Col span={4}>
                <Button type="primary" onClick={() => {
                    setID('_' + Math.random().toString(36).substr(2, 9))
                    history.push("/")
                }}>
                    Reset
                </Button>
            </Col>
            <Col>
                {server} Status:{serverStatus && <CheckCircle style={{fill: "green"}}/>} {!serverStatus &&
            <Error style={{fill: "orange"}}/>}
            </Col>

        </Row>

    )
}