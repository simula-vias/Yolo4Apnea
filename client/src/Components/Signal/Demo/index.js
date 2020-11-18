import {useEffect} from 'react';

import demo_abdo from "../../../res/demo_abdo.json"


export const Demo = ({setAbdoSignal}) => {
    useEffect(() => {
        let demo_abdo_values = demo_abdo
        console.log("demo mode set")
        setAbdoSignal([...demo_abdo_values])
    }, [setAbdoSignal])


    return null
}