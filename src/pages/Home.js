import React, { useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { Info } from './Info';
import { Routes, Route } from 'react-router-dom';
import '../App.css';
import { AboutUs } from './AboutUs';

export function Home() {


    const nameInput = "test name"
    const acceptableNames = ['TEST NAME']

    useEffect(() => {
        if (acceptableNames.includes(nameInput.toUpperCase())) {
        document.body.style.overflowY = 'auto';
        } else {
        document.body.style.overflowY = 'hidden';
        }
    }, [nameInput]);

    // const handleNameInput() {

    // }


    return (

        <>
        <GenericHeader classname="h-screen transfom-scale-5">

            <div class= "egg backdrop-blur-xl" />
            <input placeholder="Full name?"
                value={nameInput}
                // onInput={(e)=>dispatch(rsvpCodeInput(e.target.value))}
                />
                {/* onInput={(e)=>dispatch({type: "rsvpCodeInput", payload: e.target.value})}/> */}

        </GenericHeader>
        <div classname="container">
            <main className="card-stack">

                <Routes>
                    {/* <Route path="/" element={<Info/>} /> */}
                    <Route path="/" element={<AboutUs/>} />
                </Routes>

            </main>
        </div>
        </>
        
    )
}
