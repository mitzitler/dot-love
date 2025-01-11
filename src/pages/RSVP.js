import React, { useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { RSVPFormResponse } from './RSVPPages/RSVPFormResponse.js'; //RSVP.js  /RSVPPages/RSVPFormResponse.js
import { RSVPFormContact } from './RSVPPages/RSVPFormContact.js';
import { RSVPFormDietary } from './RSVPPages/RSVPFormDietary.js';
import { RSVPFormSubmit } from  './RSVPPages/RSVPFormSubmit.js';
import { Routes, Route } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { rsvpCodeInput } from '../features/guest/rsvpSlice';
import '../App.css';

export function RSVP() {

    const dispatch = useDispatch();

    const pageMainColor = "amber"
    const pageSection = "rsvp"
    const acceptableCodes = ['ABC', 'DEF', 'GHI']

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode) 

    useEffect(() => {
        if (acceptableCodes.includes(rsvpCode.toUpperCase())) {
        document.body.style.overflowY = 'auto';
        } else {
        document.body.style.overflowY = 'hidden';
        }
    }, [rsvpCode]);

    console.log("code = ", rsvpCode)

    const rsvpString = "Hi"
    const contactString = "Yo"

    // const rsvpString = rsvp === "attending" ? "We are excited you are coming!" :
    //     "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    // const contactString = "Hi " + firstName + " " + lastName + " (" + pronouns + "), " +
    //     "we can reach you at " + phoneNumber + " or " + email + " and your mailing address is " + 
    //     streetAddress + " " + secondAddress + ", in " + city + ", " + zipcode + " - " + 
    //     stateProvince + ", " + country 
    
    // function dietaryToWords(dietaryState, dietaryName) {
    //     const verb = dietaryState ? "do" : "don't"
    //     return "I " + verb + " " + dietaryName
    // }

    // function moreRestrictionsToWords(moreRestrictions) {
    //     if (moreRestrictions.length === 0) 
    //         return("")
    //     else return "; and I have other restrictions, such as " + moreRestrictions
    // }

    // const dietaryString = dietaryToWords(drinkAlcohol, "drink alcohol") + "; " +
    //     dietaryToWords(eatMeat, "eat meat") + "; " +
    //     dietaryToWords(eatDairy, "have dairy") + "; " +
    //     dietaryToWords(eatFish, "eat fish") + "; " +
    //     dietaryToWords(eatShellfish, "eat shellfish") + "; " +
    //     dietaryToWords(eatEggs, "eat eggs") + "; " +
    //     dietaryToWords(eatGluten, "eat gluten products") + "; " +
    //     dietaryToWords(eatPeanuts, "eat peanuts and legumes") +
    //     moreRestrictionsToWords(moreRestrictions)

    const dietaryString = "Lol"

    return (

        <>
        <GenericHeader classname="h-screen transfom-scale-5">

            <div class= "egg backdrop-blur-xl" />
            <input placeholder="RSVP code?"
                value={rsvpCode}
                onInput={(e)=>dispatch(rsvpCodeInput(e.target.value))}/>

            {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
        </GenericHeader>
        <div classname="container">
            <main className="card-stack">

                <Routes>
                    <Route path="/" element={
                        <RSVPFormResponse rsvpCode={rsvpCode} pageMainColor={pageMainColor} pageSection={pageSection} />} />

                    <Route path="/contact" element={
                        <RSVPFormContact pageMainColor={pageMainColor} pageSection={pageSection} />} />

                    <Route path="/dietary" element={
                        <RSVPFormDietary pageMainColor={pageMainColor} pageSection={pageSection} />} />

                    <Route path="/submit" element={
                        <RSVPFormSubmit pageMainColor={pageMainColor} pageSection={pageSection} />} />
                        
                </Routes>

            </main>
        </div>
        </>
        
    )
}

// and maybe next what i do is, scrolltrigger to make the circle size down as it slides up
// and then it lives at the top of the screen at 0.25 scale
// and the other cars on the screen are slighly smaller