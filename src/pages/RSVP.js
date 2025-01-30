import React from 'react';
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
                icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30 }} alt='💕' />
            })
        }
    }

    const pageMainColor = "amber"
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "raspberry"

    const pageSection = "rsvp"

    // fzn - single
    // unf - open plus one
    // nzu - closed plus one
    const acceptableCodes = ['FZN', 'UNF', 'NZU']

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode) 

    return (

        <>
        {/* Toast */}
        <ToastContainer
            position="top-right"
            toastStyle={{}}/>

        <GenericHeader classname="h-screen transfom-scale-5">
            <div class= "egg backdrop-blur-xl" />
            <input placeholder="RSVP code?"
                value={rsvpCode} pattern="[A-Za-z]*"
                onInput={(e)=>dispatch(rsvpCodeInput(e.target.value))}/>

            {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
        </GenericHeader>

        { acceptableCodes.includes(rsvpCode.toUpperCase()) ?
        <div classname="container">
            <main className="card-stack">
                { notify("Code accepted! Please Scroll down", true) }
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
        : <></>
        }
        </>
        
    )
}
