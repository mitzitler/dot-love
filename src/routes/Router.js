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

export function Router ({ loginHeader, setLoginHeader}) {

    const dispatch = useDispatch();

    // const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 


    // router is only ever called if login success is true, i wonder if I can 
    // call these funcs here and make them default login success = true?
    
    // dispatch(setloginHeaderState(loginHeader));
    const registryItems = useRegistryItems(true, loginHeader)
    console.log(registryItems)
    const claimedItems = useClaimedItems(true, loginHeader)
    console.log(claimedItems)

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
                            loginHeader={loginHeader} />
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