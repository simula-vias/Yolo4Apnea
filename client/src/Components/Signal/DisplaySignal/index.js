import {useEffect} from "react";


export const DisplaySignal = ({play, displayEnd, setDisplayEnd, displayStart, setDisplayStart, slidingWindow}) => {


    useEffect(() => {
        const interval = setInterval(() => {
            if (play) {
                if (displayEnd < slidingWindow) {
                    setDisplayEnd(displayEnd + 1)
                } else {
                    setDisplayEnd(displayEnd + 1)
                    setDisplayStart(displayStart + 1)
                }
            }
        }, 10) // 100 is default value
        return () => clearInterval(interval)


    }, [play, displayStart, displayEnd, setDisplayEnd,setDisplayStart,slidingWindow])


    return (null)
}