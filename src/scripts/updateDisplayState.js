export function updateDisplayState(play, displayEnd, slidingWindow, setDisplayEnd, setLastViewedIndex) {
    if (play) {
        setLastViewedIndex(displayEnd + 1)
        setDisplayEnd(displayEnd + 1)
    }
}