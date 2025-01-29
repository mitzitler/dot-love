import React, { useState, useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { GenericHeader2 } from '../components/GenericHeader2';
import { Info } from './Info';
import { AboutUs } from './AboutUs';
import { Routes, Route } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fullNameCodeInput } from '../features/guest/userSlice';
import '../App.css';

export function Home() {

    const dispatch = useDispatch();
    const [entryValue, setEntryValue] = useState("")
    const fullNameCode = useSelector((state) => state.user.fullNameCode) 
    // this needs to be a api lookup
    const acceptableNames = ['TEST NAME']

    // useEffect(() => {
    //     if (acceptableNames.includes(nameInput.toUpperCase())) {
    //     document.body.style.overflowY = 'auto';
    //     } else {
    //     document.body.style.overflowY = 'hidden';
    //     }
    // }, [nameInput]);

    // const handleNameInput() {

    // }

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
            setEntryValue={setEntryValue}
            />
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
