import React, { useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { Info } from './Info';
import { Routes, Route } from 'react-router-dom';
import '../App.css';
import { AboutUs } from './AboutUs';

export function Home() {

    return (

        <>
        <GenericHeader classname="h-screen transfom-scale-5">

            <div class= "egg backdrop-blur-xl" />
            <input placeholder="Full name?"/>
                {/* onInput={(e)=>dispatch({type: "rsvpCodeInput", payload: e.target.value})}/> */}

        </GenericHeader>
        <div classname="container">
            <main className="card-stack">

                <Routes>
                    <Route path="/" element={<Info/>} />
                    {/* <Route path="/aboutus" element={<AboutUs/>} /> */}
                </Routes>

            </main>
        </div>
        </>
        
    )
}
