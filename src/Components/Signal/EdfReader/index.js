import React from 'react';
import {EdfDecoder} from "edfdecoder";

export const EdfReader = ({setAbdoSignal}) => {

    function setNewEDFFile(event) {
        console.log("Setting new edf file")

        let file = event.target.files[0];
        let reader = new FileReader();

        reader.onload = (file) => {
            let edf = file.target.result
            let decoder = new EdfDecoder();

            decoder.setInput(edf)
            decoder.decode();
            let edfData = decoder.getOutput();

            let abdo_index = 9
            let abdoSignal = edfData.getPhysicalSignalConcatRecords(abdo_index)

            setAbdoSignal([...abdoSignal])
        }

        reader.readAsArrayBuffer(file);

    }

    return (
        <input type="file" name="file"
               onChange={setNewEDFFile}
        />
    )
}