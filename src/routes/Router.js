import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Routes, Route } from 'react-router-dom';
import { Transitionizer } from '../components/Transitionizer';
import { Info } from '../pages/Info';
import { RegistryTemp } from '../pages/RegistryTemp';
import { Registry } from '../pages/Registry';
import { AboutUs } from '../pages/AboutUs';
import { setloginHeaderState } from '../features/guest/extrasSlice';
import useRegistryItems from '../components/useRegistryItems';
import useClaimedItems from '../components/useClaimedItems';

export function Router ({ setLoginHeader}) {

    // const dispatch = useDispatch();

    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 
    const loginHeader = { 'X-First-Last': loginHeaderState}

    // dispatch(setloginHeaderState(loginHeader));
    const registryItems = useRegistryItems(true, loginHeaderState)
    const claimedItems = useClaimedItems(true, loginHeaderState)

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
            <Route
                path="/registry"
                element={
                    <Transitionizer>
                        <Registry 
                            registryItems={registryItems} 
                            claimedItems={claimedItems}
                            />
                    </Transitionizer>
                }
            />
            <Route
                path="/about"
                element={
                    <Transitionizer>
                        <AboutUs />
                    </Transitionizer>
                }
            />
            {/* <Route
                path="/tempregistry"
                element={
                    <Transitionizer>
                        <RegistryTemp 
                            registryItems={registryItems} 
                            claimedItems={claimedItems} />
                    </Transitionizer>
                }
            /> */}
        </Routes>
    )
}

export default Router;

// is this the same as export default Router