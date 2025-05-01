import React from 'react';
import {Routes, Route} from 'react-router-dom';

import { Transitionizer } from '../components/Transitionizer';
import { Info } from '../pages/Info';
import { RegistryTemp } from '../pages/RegistryTemp';
import { InfoDressCode } from '../pages/InfoPages/InfoDressCode.js'
import { Registry } from '../pages/Registry';
import { AboutUs } from '../pages/AboutUs';
// import Thanks from '../pages/Thanks';
import {Data} from '../pages/Data';

export function Router () {
    return (
        <Routes>
            {/* <Route
                index
                element={
                    <Transitionizer>
                        <RSVP />
                    </Transitionizer>
                }
            /> */}
            <Route
                path="/"
                element={
                    <Transitionizer>
                        <Info />
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
            {/* <Route
                path="/info/dresscode"
                element={
                    <Transitionizer>
                        <InfoDressCode />
                    </Transitionizer>
                }
            /> */}
            {/* <Route
                path="/registry"
                element={
                    <Transitionizer>
                        <Registry />
                    </Transitionizer>
                }
            /> */}
            <Route
                path="/about"
                element={
                    <Transitionizer>
                        <AboutUs />
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
            {/* <Route
                path="/data"
                element={
                    <Transitionizer>
                        <Data />
                    </Transitionizer>
                }
            /> */}

            <Route
                path="/tempregistry"
                element={
                    <Transitionizer>
                        <RegistryTemp />
                    </Transitionizer>
                }
            />
        </Routes>
    )
}

export default Router;

// is this the same as export default Router