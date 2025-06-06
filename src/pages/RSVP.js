import React from 'react';
import { useEffect } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { RSVPFormResponse } from './RSVPPages/RSVPFormResponse.js'; //RSVP.js  /RSVPPages/RSVPFormResponse.js
import { RSVPFormContact } from './RSVPPages/RSVPFormContact.js';
import { RSVPFormDietary } from './RSVPPages/RSVPFormDietary.js';
import { RSVPFormSubmit } from  './RSVPPages/RSVPFormSubmit.js'; // ignore error
import { RSVPFormPlusOne } from  './RSVPPages/RSVPFormPlusOne.js';
import { RSVPFormConfirmation } from  './RSVPPages/RSVPFormConfirmation.js'; // ignore error
import { Routes, Route } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { rsvpCodeInput, guestCodeInput } from '../features/guest/rsvpSlice';
import '../App.css';

export function RSVP() {

    const dispatch = useDispatch();

    // handle guest code query param
    const [searchParams] = useSearchParams();
    const guestCode = useSelector((state) => state.rsvp.guestCode) 
    const code = guestCode ? guestCode : searchParams.get('code') 
    dispatch(guestCodeInput(code))

    const pageMainColor = "amber"
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "raspberry"

    const pageSection = "rsvp"

    // fzn - single
    // unf - open plus one
    // nzu - closed plus one
    const acceptableCodes = ['FZN', 'UNF', 'NZU']

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode) 
    const isAllowed = acceptableCodes.includes(rsvpCode.toUpperCase()) || code

    console.log("code is:", code)
    console.log("guestcode is:", guestCode)

    useEffect(() => {
        const preventScroll = (event) => {
          event.preventDefault();
        };
    
        if (!isAllowed) {
          window.addEventListener("wheel", preventScroll, { passive: false });
          window.addEventListener("touchmove", preventScroll, { passive: false });
          window.addEventListener("keydown", (event) => {
            if (["ArrowUp", "ArrowDown", "Space", "PageUp", "PageDown"].includes(event.key)) {
              preventScroll(event);
            }
          });
        } else {
          window.removeEventListener("wheel", preventScroll);
          window.removeEventListener("touchmove", preventScroll);
          window.removeEventListener("keydown", preventScroll);
        }
    
        return () => {
          window.removeEventListener("wheel", preventScroll);
          window.removeEventListener("touchmove", preventScroll);
          window.removeEventListener("keydown", preventScroll);
        };
      }, [isAllowed]);

    return (

        <>
        {code ?
             <GenericHeader classname="h-screen transfom-scale-5">
             <div class= "egg backdrop-blur-xl" />
             <input placeholder="Welcome" />
 
             {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
             </GenericHeader>
             
             : 
             <GenericHeader classname="h-screen transfom-scale-5">
             <div class= "egg backdrop-blur-xl" />
             <input placeholder="RSVP code?"
                 value={rsvpCode} pattern="[A-Za-z]*"
                 onInput={(e)=>dispatch(rsvpCodeInput(e.target.value))
                 }/>
 
             {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
             </GenericHeader>
        }


        { isAllowed ?
        <div classname="container">
            <main className="rsvp-card-stack">
                <Routes>
                    {/* Entrypoint for normal guests */}
                    <Route path="/" element={
                        <RSVPFormResponse rsvpCode={rsvpCode} pageMainColor={pageMainColor} 
                        pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}
                        pageSection={pageSection} />} />

                    {/* Entrypoint for plus-ones */}
                    <Route path="/guest" element={
                        <RSVPFormPlusOne pageMainColor={pageMainColor}
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
