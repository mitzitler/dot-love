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

    // console.log('home.js ...', loginSuccess)

    // Function to emit toast 🍞
    // const notify = (input) => {
    //     toast.info(input, {
    //         theme: "dark",
    //         position: "top-right",
    //         icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30 }} alt='💕' />
    //     })
    // }

    // const location = useLocation();
    // useEffect(() => {
    //     window.scrollTo(0, 0); 
    // }, [location.pathname]);

    // // API Call - triggers only when loginHeader changes
    // const { data, error, isLoading } = useGetUserQuery(loginHeader, {
    //     skip: !loginHeader, // Skip API call if header is null
    // });

    // useEffect(() => {
    //     if (data && data.code === 200) {
    //         setLoginSuccess(true);
    //         console.log("Gizmo login success, result:", data);
    //         notify(`Welcome, ${data.body.user.first}! Please scroll down`)
    //     }
    //     if (error) {
    //         console.error("Login API call failed:", error);
    //     }
    // }, [data, error]);

    // const handleKeyDown = (event) => {
    //     if (event.key === 'Enter') {
    //       event.preventDefault()
    //     }
    //   };

    // const handleNameChange = (e) => {
    //     const value = e.target.value;
    //     setEntryValue(value);

    //     const [first, last] = value.trim().split(" ");
    //     if(e.keyCode == 13){ 
    //         e.preventDefault();
    //      }

    //     if (first && last) {
    //         const firstLast = `${first}_${last}`;
    //         setLoginHeader({ 'X-First-Last': firstLast });
    //     } else {
    //         setLoginHeader(null); // Prevent invalid API calls
    //     }
    // };

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
