import React, { useState, useEffect, useReducer } from 'react';
import { GenericHeader2 } from '../components/GenericHeader2';
import { Info } from './Info';
import { AboutUs } from './AboutUs';
import { Routes, Route } from 'react-router-dom';
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

    if (acceptableNames.includes(fullNameCode.toUpperCase()))
        console.log('name accepted')
    else 
        console.log('name not accepted')

    return (

        <>
        <GenericHeader2 classname="h-screen transfom-scale-5" 
            placeholder={"Full name?"} entryValue={entryValue} 
            setEntryValue={setEntryValue}/>
        { acceptableNames.includes(fullNameCode.toUpperCase()) ?
        <div classname="container">
            <main className="card-stack">

                <Routes>
                    <Route path="/" element={<Info/>} />
                    <Route path="/info" element={<Info/>} />
                    <Route path="/aboutus" element={<AboutUs/>} />
                </Routes>

            </main>
        </div>
        : <></>
        }
        </>
        
    )
}
