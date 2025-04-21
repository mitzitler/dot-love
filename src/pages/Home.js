import React, { useState, useEffect, useReducer } from 'react';
import { GenericHeader2 } from '../components/GenericHeader2';
import { Router } from '../routes/Router'
import { HeaderHome } from './HeaderHome';
// import { HomePageRoutes } from '../routes/HomePageRoutes';
import { Info } from './Info';
import { AboutUs } from './AboutUs';
import { Routes, Route, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useGetUserQuery } from '../services/gizmo.js';
import { toast } from 'react-toastify'; // Toast (yum!)
import '../App.css';
import { Transitionizer } from '../components/Transitionizer.js';

export function Home() {

    // const dispatch = useDispatch();
    const [entryValue, setEntryValue] = useState("")
    // const fullNameCode = useSelector((state) => state.user.fullNameCode) 

    // const entryValuePlaceholder = "First Last"
    // const [loginHeader, setLoginHeader] = useState(null);
    const [loginSuccess, setLoginSuccess] = useState(false);

    const [loginSuccess, setLoginSuccess] = useState(false);


    return (
        <>
        {/* TODO: only letters can be accepted */}

        {/* <GenericHeader2 classname="h-screen transfom-scale-5" 
            placeholder={"Full name"} entryValue={entryValue} 
            setEntryValue={setEntryValue}/> */}
        <HeaderHome classname="h-screen transfom-scale-5" 
            // placeholder={"Full name"}entryValue={entryValue} 
            // setEntryValue={setEntryValue}
            loginSuccess={loginSuccess}
            setLoginSuccess={setLoginSuccess}
            />
            
        { loginSuccess ?
        <div classname="container">
            <main className="card-stack">
                    {/* <Transitionizer> */}
                    <Routes>
                        <Route path="/" element={<Info/>}/>
                        <Route path="info" element={<Info/>}/>
                        <Route path="about" element={<AboutUs/>}/>
                        
                    </Routes>
                    {/* </Transitionizer> */}
                    {/* <HomePageRoutes/> */}
                    {/* <Router /> */}
            </main>
        </div>
        
        : <></>
        }
        
        </>
    )
}
