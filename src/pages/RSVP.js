import React, { useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { RSVPFormResponse } from './RSVPPages/RSVPFormResponse.js'; //RSVP.js  /RSVPPages/RSVPFormResponse.js
import { RSVPFormContact } from './RSVPPages/RSVPFormContact.js';
import { RSVPFormDietary } from './RSVPPages/RSVPFormDietary.js';
import { RSVPFormSubmit } from  './RSVPPages/RSVPFormSubmit.js'; // ignore error
import { RSVPFormConfirmation } from  './RSVPPages/RSVPFormConfirmation.js'; // ignore error
import { Routes, Route } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { rsvpCodeInput } from '../features/guest/rsvpSlice';
import { ToastContainer, toast } from 'react-toastify'; // Toast (yum!)
import '../App.css';

export function RSVP() {

    const dispatch = useDispatch();

    const notify = (input, success) => {
        if (success) {
            toast.info(input, {
                theme: "dark",
                position: "top-right",
                icon: ({theme, type}) =>  <img src=""/>
            })
        }
    }

    const pageMainColor = "amber"
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "raspberry"
    const pageSection = "rsvp"
    const acceptableCodes = ['ABC', 'DEF', 'GHI']

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode) 

    useEffect(() => {
        if (acceptableCodes.includes(rsvpCode.toUpperCase())) {
            document.body.style.overflowY = 'auto';
            notify("Code accepted! Please scroll down", true);
        } else {
            document.body.style.overflowY = 'hidden';
        }
    }, [rsvpCode]);

    return (

        <>
        {/* Toast */}
        <ToastContainer
            position="top-right"
            toastStyle={{}}/>

        <GenericHeader classname="h-screen transfom-scale-5">
            <div class= "egg backdrop-blur-xl" />
            <input placeholder="RSVP code?"
                value={rsvpCode}
                onInput={(e)=>dispatch(rsvpCodeInput(e.target.value))}/>

            {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
        </GenericHeader>
        <div classname="container">
            <main className="card-stack">
                
                {/* <div className={`section-content swipe-card flex-grow bg-lime-400/75 border-lime-500/50 border-2 backdrop-blur-md`}> */}
                {/* </div> */}

                <Routes>
                    <Route path="/" element={
                        <RSVPFormResponse rsvpCode={rsvpCode} pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />

                    <Route path="/contact" element={
                        <RSVPFormContact pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />

                    <Route path="/dietary" element={
                        <RSVPFormDietary pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />

                    <Route path="/submit" element={
                        <RSVPFormSubmit pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />

                    <Route path="/confirmation" element={
                        <RSVPFormConfirmation pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />
                        
                </Routes>

            </main>
        </div>
        </>
        
    )
}

// and maybe next what i do is, scrolltrigger to make the circle size down as it slides up
// and then it lives at the top of the screen at 0.25 scale
// and the other cars on the screen are slighly smaller
