import React, {useEffect} from "react";


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


    return (
        <>
            Display signal starts at {displayStart} and ends at {displayEnd}
            Play state = {play.toString()}
        </>
    )
}