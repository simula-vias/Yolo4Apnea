import React from 'react';
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import ButtonGroup from "@material-ui/core/ButtonGroup";


export const Configuration = ({demoMode, setDemoMode, play, setPlay}) => {
    return (
        <>


            <Grid item xs={12} container justify="center">
                <ButtonGroup color="primary" aria-label="outlined primary button group">
                    <Button>Connect Abdo sensor</Button>
                    <Button>Connect Thor sensor</Button>
                </ButtonGroup>
            </Grid>

            <Grid item xs={12} container justify="center">
                <Button variant="contained" color="secondary"
                        onClick={() => setDemoMode(!demoMode)}
                >Demo</Button>

            </Grid>

            <Grid item xs={12} container justify="center">
                <input type="file" name="file"
                    //onChange={onChangeHandler}
                />

            </Grid>

            <Grid item xs={12} container justify="center">
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                        setPlay(!play)
                    }}
                >
                    Play EDF
                </Button>


            </Grid>

            <>
                Configuration: Demo mode is {demoMode.toString()}
            </>
        </>

    )
}