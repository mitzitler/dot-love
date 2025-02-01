import React, { useState, useEffect, useReducer } from 'react';
import { GenericHeader2 } from '../components/GenericHeader2';
import { HomePageRoutes } from '../routes/HomePageRoutes';
import { Info } from './Info';
import { AboutUs } from './AboutUs';
import { Routes, Route, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import '../App.css';

export function Home() {

    const dispatch = useDispatch();
    const [entryValue, setEntryValue] = useState("")
    const fullNameCode = useSelector((state) => state.user.fullNameCode) 
    // this needs to be a api lookup
    const acceptableNames = ['TEST NAME']

    console.log(fullNameCode)
    console.log(acceptableNames)

    const location = useLocation();
    useEffect(() => {
        window.scrollTo(0, 0); 
    }, [location.pathname]);

    if (acceptableNames.includes(fullNameCode.toUpperCase()))
        console.log('name accepted')
    else 
        console.log('name not accepted')

    return (

        <>
        {/* TODO: only letters can be accepted */}
        <GenericHeader2 classname="h-screen transfom-scale-5" 
            placeholder={"Full name"} entryValue={entryValue} 
            setEntryValue={setEntryValue}/>
        { acceptableNames.includes(fullNameCode.toUpperCase()) ?
        <div classname="container">
            <main className="card-stack">
                
                    {/* <Route path="/" element={<Info/>}/> */}
                    <HomePageRoutes/>
            </main>
        </div>
        : <></>
        }
        </>
        
    )
}
