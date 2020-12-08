import {EdfDecoder} from "edfdecoder";

export function setNewEdfFile(event,setFunction){
    console.log("Reading edf file")

    let edf = event.target.result
    let decoder = new EdfDecoder();

    decoder.setInput(edf)
    decoder.decode();
    let edfData = decoder.getOutput();

    let abdo_index = 9
    let abdoSignal = edfData.getPhysicalSignalConcatRecords(abdo_index)

    setFunction([...abdoSignal], "EDF")


}