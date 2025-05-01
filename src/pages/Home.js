import React, { useState } from 'react';
import { Router } from '../routes/Router'
import { HeaderHome } from './HeaderHome';
import '../App.css';

export function Home() {

    const [loginSuccess, setLoginSuccess] = useState(false);


    return (
        <>
        <HeaderHome className="h-screen transfom-scale-5" 
            loginSuccess={loginSuccess}
            setLoginSuccess={setLoginSuccess}
            />
            
        { loginSuccess ?
        <div className="container">
            <main className="card-stack">

                    <Router />
            </main>
        </div>
        
        : <></>
        }
        
        </>
    )
}
