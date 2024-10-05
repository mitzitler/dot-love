import React from 'react';
import {Routes, Route} from 'react-router-dom';

import {Transitionizer} from '../components/Transitionizer';
import {RSVP} from '../pages/RSVP';
import {Info} from '../pages/Info';
import {Registry} from '../pages/Registry';
import {About} from '../pages/About';
// import Thanks from '../pages/Thanks';
import {Data} from '../pages/Data';

const Router = () => {
    return (
        <Routes>
            <Route
                index
                element={
                    <Transitionizer>
                        <RSVP />
                    </Transitionizer>
                }
            />
            <Route
                path="/info"
                element={
                    <Transitionizer>
                        <Info />
                    </Transitionizer>
                }
            />
            <Route
                path="/registry"
                element={
                    <Transitionizer>
                        <Registry />
                    </Transitionizer>
                }
            />
            <Route
                path="/about"
                element={
                    <Transitionizer>
                        <About />
                    </Transitionizer>
                }
            />
            {/* <Route
                path="/thanks"
                element={
                    <Transitionizer>
                        <Thanks />
                    </Transitionizer>
                }
            /> */}
            <Route
                path="/data"
                element={
                    <Transitionizer>
                        <Data />
                    </Transitionizer>
                }
            />
        </Routes>
    )
}

export default Router;

// is this the same as export default Router