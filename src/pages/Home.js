import React, { useState } from 'react';
import { Router } from '../routes/Router'
import { HeaderHome } from './HeaderHome';
import useRegistryItems from '../components/useRegistryItems.js';
import '../App.css';

export function Home() {

    const [loginSuccess, setLoginSuccess] = useState(false);

    let loginHeaderHard = 'mitzi_zitler'
    const registryItems = useRegistryItems(loginSuccess, loginHeaderHard)
    console.log(registryItems)

    return (
        <>
        <HeaderHome className="h-screen transfom-scale-5" 
            loginSuccess={loginSuccess}
            setLoginSuccess={setLoginSuccess}
            />
            
        { loginSuccess ?
        <div className="container">
            <main className="card-stack">

                    <Router registryItems={registryItems} />
            </main>
        </div>
        
        : <></>
        }
        
        </>
    )
}
