import React from 'react';
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import {EdfReader} from "../Signal/EdfReader";
import {predict_whole_signal} from "../Signal/PredictedSignal/apiCalls";


export const Configuration = ({demoMode, setDemoMode, play, setPlay,setAbdoSignal,abdoSignal,apiRoot,id,setPredictions,setDisplayEnd}) => {

    function analyze_recording() {
        predict_whole_signal(abdoSignal,apiRoot,id)
            .then((pred) => {
                setPredictions(pred)
                setDisplayEnd(abdoSignal.length)
                }
            )
    }


    return (
        <>


            <Grid item xs={12} container justify="center">
                <ButtonGroup color="primary" aria-label="outlined primary button group">
                    <Button>Connect Abdo sensor</Button>
                    <Button>Connect Thor sensor</Button>
                </ButtonGroup>
            </Grid>


            <Grid container justify={"center"} spacing={2} >
                <Grid item>
                    <Button variant="contained" color="secondary"
                            onClick={() => setDemoMode(!demoMode)}
                    >Demo</Button>
                </Grid>

                <Grid item>

                <EdfReader setAbdoSignal={setAbdoSignal}/>
                </Grid>
            </Grid>
            {abdoSignal && <Grid container justify={"center"} spacing={2}>
                <ButtonGroup>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => {
                            setPlay(!play)
                        }}
                    >
                        Play EDF
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={analyze_recording}>
                        Analyze recording
                    </Button>
                </ButtonGroup>


            </Grid>}



        </>

    )
}