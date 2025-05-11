import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { Router } from '../routes/Router'
import { HeaderHome } from './HeaderHome';
import useRegistryItems from '../components/useRegistryItems.js';
import useClaimedItems from '../components/useClaimedItems.js'
import '../App.css';

export function Home({ loginHeader, setLoginHeader }) {

    const [loginSuccess, setLoginSuccess] = useState(false);
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    return (
        <>
        <HeaderHome className="h-screen transfom-scale-5" 
            loginSuccess={loginSuccess}
            setLoginSuccess={setLoginSuccess}
            loginHeader={loginHeader}
            setLoginHeader={setLoginHeader}
            />
            
        { loginSuccess ?
        <div className="container">
            <main className="card-stack">

                    {/* <Router registryItems={registryItems} claimedItems={claimedItems} /> */}
                    {/* <Router loginHeader={loginHeader} setLoginHeader={setLoginHeader} /> */}
                    <Router/>
            </main>
        </div>
        
        : <></>
        }
        
        </>
    )
}
