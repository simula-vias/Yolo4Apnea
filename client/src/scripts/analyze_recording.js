import {predictWholeSignal} from "./predictWholeSignal";


export function analyze_recording(setPredictions,setDisplayEnd,abdoSignal,updatePredictions,server,id,setPredictionDF) {
    predictWholeSignal(abdoSignal,server,id)
        .then((pred) => {
                setPredictions(pred)
                setDisplayEnd(abdoSignal.length)
                updatePredictions(server,id,setPredictionDF)
            }
        )
}