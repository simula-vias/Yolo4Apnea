import React, {useState} from 'react';
import {BrowserRouter,Switch,Route} from "react-router-dom";
import {MainRoute} from "./Routes/MainRoute";
import ServerContext from "./utils/ServerContext";
import SignalContext from "./utils/SignalContext";
import {DisplayRoute} from "./Routes/DisplayRoute";


function App() {
    const [server,setServer] = useState("http://localhost:5000")
    const [signalObject,setSignalObject] = useState(
        {sensor:null,
            abdoSignal : []
    })


    return (
        <ServerContext.Provider value={{server,setServer}}>
            <SignalContext.Provider value={{signalObject,setSignalObject}}>
                <BrowserRouter>
                    <Switch>
                        <Route path="/display">
                            <DisplayRoute/>
                        </Route>
                        <Route path="/">
                            <MainRoute>
                            </MainRoute>
                        </Route>
                    </Switch>
                </BrowserRouter>
            </SignalContext.Provider>
        </ServerContext.Provider>



    );
}

export default App;
