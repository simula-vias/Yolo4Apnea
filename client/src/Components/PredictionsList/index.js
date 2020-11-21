import React, {useState} from "react";
import Grid from "@material-ui/core/Grid";
import {Button, TableBody, TableHead} from "@material-ui/core";
import TableContainer from "@material-ui/core/TableContainer";
import Table from "@material-ui/core/Table";
import TableRow from "@material-ui/core/TableRow";
import TableCell from '@material-ui/core/TableCell';

export const PredictionList = ({apiRoot,id}) => {

    const [predictionDF,setPredictionDF] = useState()



    function updatePredictions()  {
        console.log("UPDATING PREDICTIONS")
        let apiEndpoint = apiRoot + "/predictions"

        let requestData = {id:id}

        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        }

        fetch(apiEndpoint, requestOptions)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(response.status)
                }
                else if (response.status === 204){
                    return {}
                }
                else {
                    return response.json()
                }
            })
            .then(dataframe => {
                if (Object.keys(dataframe).length > 0){
                    setPredictionDF(dataframe)
                }
            })
            .catch((error) =>{
                console.log(error)
            })
    }

    return (
        <>
            <Grid item>
                List of predictions
                <Button onClick={updatePredictions}> Update predictions</Button>
                {predictionDF && <TableContainer >
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Start</TableCell>
                                <TableCell>End</TableCell>
                                <TableCell>Min confidence</TableCell>
                                <TableCell>Duration</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            { Object.keys(predictionDF).map((row) => (
                                <TableRow key={row}>
                                    <TableCell>{predictionDF[row]["start"]} </TableCell>
                                    <TableCell>{predictionDF[row]["end"]} </TableCell>
                                    <TableCell>{predictionDF[row]["min_confidence"]} </TableCell>
                                    <TableCell>{predictionDF[row]["duration"]} </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>

                </TableContainer>}
            </Grid>
        </>
    )
}