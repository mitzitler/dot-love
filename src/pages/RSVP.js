import React, { useEffect, useReducer } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { RSVPFormResponse } from './RSVPPages/RSVPFormResponse'
import { RSVPFormContact } from './RSVPPages/RSVPFormContact'
import { RSVPFormDietary } from './RSVPPages/RSVPFormDietary'
import { RSVPFormSubmit } from './RSVPPages/RSVPFormSubmit'
import { Routes, Route } from 'react-router-dom';
import '../App.css';

// to do:

// animate on click dietary

// create store
// create blinking eye animation
// move assets to s3 bucket

// create homepage flow


const initalState = {
    // could be 'ABC', 'DEF', 'GHI'
    // rsvpCode: localStorage.getItem("rsvpCode") || "", 
    rsvpCode: '',
    // 'undecided', 'attending', 'notattenting'
    rsvp: 'undecided', 
    firstName: "", 
    lastName: "", 
    pronouns: "", 
    phoneNumber: "", 
    email: "", 
    streetAddress: "", 
    secondAddress: "", 
    city: "", 
    zipcode: "",    
    country: "", 
    stateProvince: "", 
    canContinueDietary: false,
    drinkAlcohol: true, 
    eatMeat: true, 
    eatDairy: true,
    eatFish: true, 
    eatShellfish: true, 
    eatEggs: true, 
    eatGluten: true, 
    eatPeanuts: true, 
    moreRestrictions: "",
    submitted: null
}

// addtl items: plusOneLink

function reducer(state, action) {
    switch (action.type) {
        case "rsvpCodeInput": 
            localStorage.setItem("rsvpCode", action.payload);
            return {
                ...state, 
                rsvpCode: action.payload
            }
        case "rsvpInput": 
            return {
                ...state, 
                rsvp: action.payload
            };

        // case "continueContact": // this one isnt necessary
        //     return { // only allow this action if the items on the page are ready
        //     };
        
        case "firstNameInput": return {...state, firstName: action.payload};
        case "lastNameInput": return {...state, lastName: action.payload};
        case "pronounsInput": return {...state, pronouns: action.payload};
        case "phoneNumberInput": return {...state, phoneNumber: action.payload};
        case "emailInput": return {...state, email: action.payload};
        case "streetAddressInput": return {...state, streetAddress: action.payload};
        case "secondAddressInput": return {...state, secondAddress: action.payload};
        case "cityInput": return {...state, city: action.payload};
        case "zipcodeInput": return {...state, zipcode: action.payload};
        case "countryInput": return {...state, country: action.payload};
        case "stateProvinceInput": return {...state, stateProvince: action.payload};

        case "continueDietary": // but im not going to check for secondaddress
            { 
                console.log("can i continue? ", state.canContinueDietary);
                if (!state.firstName || !state.lastName || !state.pronouns || 
                  !state.phoneNumber || !state.email || !state.streetAddress || 
                  !state.city || !state.zipcode || !state.country || !state.stateProvince)
              return {...state, canContinueDietary: false} 
              else return {...state, canContinueDietary: true}
             // only allow this action if the items on the page are ready
            };
        
        case "drinkAlcoholToggle": return {...state, drinkAlcohol: !state.drinkAlcohol};
        case "eatMeatToggle": return {...state, eatMeat: !state.eatMeat};
        case "eatDairyToggle": return {...state, eatDairy: !state.eatDairy};
        case "eatFishToggle": return {...state, eatFish: !state.eatFish};
        case "eatShellfishToggle": return {...state, eatShellfish: !state.eatShellfish};
        case "eatEggsToggle": return {...state, eatEggs: !state.eatEggs};
        case "eatGlutenToggle": return {...state, eatGluten: !state.eatGluten};
        case "eatPeanutsToggle": return {...state, eatPeanuts: !state.eatPeanuts};
        case "moreRestrictionsInput": return {...state, moreRestrictions: action.payload};

        case "submitFormGC1": return {...state, submitted: action.payload};
        case "submitFormGC1.5": return {...state, submitted: action.payload};
        case "submitFormGC2": return {...state, submitted: action.payload, rsvpCode: 'ABC' }
        
        default: throw new Error("what did you do????")
    }
}

export function RSVP() {

    const pageMainColor = "amber"
    const pageSection = "rsvp"

    const [{rsvpCode, rsvp, firstName, lastName, pronouns, phoneNumber, 
        email, streetAddress, secondAddress, city, zipcode,
        country, stateProvince, canContinueDietary, drinkAlcohol, eatMeat, eatDairy,
        eatFish, eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions
    }, dispatch] = useReducer(reducer, initalState)

    const acceptableCodes = ['ABC', 'DEF', 'GHI']

    useEffect(() => {
        if (acceptableCodes.includes(rsvpCode.toUpperCase())) {
        document.body.style.overflowY = 'auto';
        } else {
        document.body.style.overflowY = 'hidden';
        }
    }, [rsvpCode]);


    console.log("code = ", rsvpCode)

    const rsvpString = rsvp === "attending" ? "We are excited you are coming!" :
        "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    const contactString = "Hi " + firstName + " " + lastName + " (" + pronouns + "), " +
        "we can reach you at " + phoneNumber + " or " + email + " and your mailing address is " + 
        streetAddress + " " + secondAddress + ", in " + city + ", " + zipcode + " - " + 
        stateProvince + ", " + country 
    
    function dietaryToWords(dietaryState, dietaryName) {
        const verb = dietaryState ? "do" : "don't"
        return "I " + verb + " " + dietaryName
    }

    function moreRestrictionsToWords(moreRestrictions) {
        if (moreRestrictions.length === 0) 
            return("")
        else return "; and I have other restrictions, such as " + moreRestrictions
    }

    const dietaryString = dietaryToWords(drinkAlcohol, "drink alcohol") + "; " +
        dietaryToWords(eatMeat, "eat meat") + "; " +
        dietaryToWords(eatDairy, "have dairy") + "; " +
        dietaryToWords(eatFish, "eat fish") + "; " +
        dietaryToWords(eatShellfish, "eat shellfish") + "; " +
        dietaryToWords(eatEggs, "eat eggs") + "; " +
        dietaryToWords(eatGluten, "eat gluten products") + "; " +
        dietaryToWords(eatPeanuts, "eat peanuts and legumes") +
        moreRestrictionsToWords(moreRestrictions)

    return (

        <>
        <GenericHeader classname="h-screen transfom-scale-5">

            <div class= "egg backdrop-blur-xl" />
            <input placeholder="RSVP code?"
                onInput={(e)=>dispatch({type: "rsvpCodeInput", payload: e.target.value})}/>

            {/* i cant tell why, but when theres an input, it jumps a few pixels to the left */}
        </GenericHeader>
        <div classname="container">
            <main className="card-stack">

                <Routes>
                    <Route path="/" element={
                        <RSVPFormResponse rsvp={rsvp} rsvpCode={rsvpCode} 
                            pageMainColor={pageMainColor} pageSection={pageSection} dispatch={dispatch} />} />

                    <Route path="/contact" element={
                        <RSVPFormContact rsvpCode={rsvpCode} firstName={firstName} lastName={lastName} 
                            pronouns={pronouns} phoneNumber={phoneNumber} 
                            email={email} streetAddress={streetAddress} secondAddress={secondAddress}
                            zipcode={zipcode} city={city} country={country} stateProvince={stateProvince} 
                            canContinueDietary={canContinueDietary} 
                            pageMainColor={pageMainColor} pageSection={pageSection} dispatch={dispatch} />} />

                    <Route path="/dietary" element={
                        <RSVPFormDietary rsvpCode={rsvpCode} drinkAlcohol={drinkAlcohol} eatMeat={eatMeat} 
                            eatDairy={eatDairy} eatFish={eatFish} eatShellfish={eatShellfish}
                            eatEggs={eatEggs} eatGluten={eatGluten} eatPeanuts={eatPeanuts} 
                            moreRestrictions={moreRestrictions} 
                            pageMainColor={pageMainColor} pageSection={pageSection} dispatch={dispatch} />} />

                    <Route path="/submit" element={
                        <RSVPFormSubmit rsvpCode={rsvpCode} contactString={contactString} 
                            firstName={firstName} lastName={lastName} pronouns={pronouns}
                            phoneNumber={phoneNumber} 
                            email={email} streetAddress={streetAddress} secondAddress={secondAddress}
                            zipcode={zipcode} city={city} country={country} stateProvince={stateProvince}
                            drinkAlcohol={drinkAlcohol} eatMeat={eatMeat} 
                            eatDairy={eatDairy} eatFish={eatFish} eatShellfish={eatShellfish}
                            eatEggs={eatEggs} eatGluten={eatGluten} eatPeanuts={eatPeanuts} 
                            moreRestrictions={moreRestrictions} dietaryString={dietaryString} 
                            pageMainColor={pageMainColor} pageSection={pageSection} dispatch={dispatch} />} />
                </Routes>

            </main>
        </div>
        </>
        
    )
}

// and maybe next what i do is, scrolltrigger to make the circle size down as it slides up
// and then it lives at the top of the screen at 0.25 scale
// and the other cars on the screen are slighly smaller