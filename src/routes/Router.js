import React, { Suspense, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Routes, Route } from 'react-router-dom';
import { Transitionizer } from '../components/Transitionizer';
import { Info } from '../pages/Info';
import { RegistryTemp } from '../pages/RegistryTemp';
import { Registry } from '../pages/Registry';
import { AboutUs } from '../pages/AboutUs';
import { Survey } from '../pages/games/militsa';
import { Pritham } from '../pages/games/pritham';
import { setloginHeaderState } from '../features/guest/extrasSlice';
import { JulesGame } from '../pages/games/julescraft';
import useRegistryItems from '../components/useRegistryItems';
import useClaimedItems from '../components/useClaimedItems';

// Admin pulls in MUI + react-virtuoso + admin-only queries that regular
// guests never need, so it's code-split out of the main bundle.
const Admin = React.lazy(() =>
    import('../pages/Admin').then((module) => ({ default: module.Admin }))
);

export function Router ({ setLoginHeader}) {

    // const dispatch = useDispatch();

    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 
    const loginHeader = { 'X-First-Last': loginHeaderState}

    // dispatch(setloginHeaderState(loginHeader));
    const registryItems = useRegistryItems(true, loginHeaderState)
    const claimedItems = useClaimedItems(true, loginHeaderState)

    const categorizePrice = (price_cents) => {
        if (price_cents == 0) return '??'
        if (price_cents > 0 && price_cents <= 7500) return '$0-75';
        if (price_cents <= 15000) return '$75-150';
        if (price_cents <= 25000) return '$150-225';
        if (price_cents <= 30000) return '$225-300';
        if (price_cents > 30000) return '$300+';
        return '$300+'
    };
      
    let registryItemsCat = Object.fromEntries(
        Object.entries(registryItems)
            .filter(([_, value]) => value.display) 
            .map(([key, value]) => [
                key,
                { ...value, price_cat: categorizePrice(value.price_cents) },
        ])
    );

    registryItemsCat = Object.entries(registryItemsCat).map(([key, item]) => ({
        ...item,
        id: key,
      }));

    let claimedItemsFilter = Object.fromEntries(
        Object.entries(claimedItems)
            .filter(([_, value]) => value.claim_state == "CLAIMED")
    )

    let claimedItemsClaimed = Object.entries(claimedItemsFilter).map(([key, item]) => ({
        ...item,
        id: key,
      }));

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
                            registryItems={registryItemsCat} 
                            claimedItems={claimedItemsClaimed}
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
            <Route
                path="/admin"
                element={
                    <Transitionizer>
                        <Suspense fallback={<div className="p-10 text-center font-suse">Loading admin…</div>}>
                            <Admin
                                registryItems={registryItemsCat}
                                claimedItems={claimedItemsClaimed}
                                />
                        </Suspense>
                    </Transitionizer>
                }
            />
            <Route
                path="/games/militsa"
                element={
                    <Transitionizer>
                        <Survey />
                    </Transitionizer>
                }
            />
            <Route
                path="/games/pritham"
                element={
                    <Transitionizer>
                        <Pritham />
                    </Transitionizer>
                }
            />
            <Route
                path="/games/jules"
                element={
                    <Transitionizer>
                        <JulesGame />
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
