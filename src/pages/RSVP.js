import React, { useReducer } from 'react';
import { RSVPFormResponse } from './RSVPpages/RSVPFormResponse'
import { RSVPFormContact } from './RSVPpages/RSVPFormContact'
import { RSVPFormDietary } from './RSVPpages/RSVPFormDietary'
import { RSVPFormSubmit } from './RSVPpages/RSVPFormSubmit'
import { Routes, Route } from 'react-router-dom';

const initalState = {
    rsvpCode: 'ABC',
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
    drinkAlcohol: true, 
    eatMeat: true, 
    eatDairy: true,
    eatFish: true, 
    eatShellfish: true, 
    eatEggs: true, 
    eatGluten: true, 
    eatPeanuts: true, 
    moreRestrictions: "",
}

function reducer(state, action) {
    switch (action.type) {
        case "rsvpInput": 
            return {
                ...state, 
                rsvp: action.payload
            };

        case "continueContact": 
            return { // only allow this action if the items on the page are ready
            };
        
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

        case "continueDietary": 
            return { // only allow this action if the items on the page are ready
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
        
        default: throw new Error("what did you do????")
    }
}

export function RSVP() {

    const [{rsvpCode, rsvp, firstName, lastName, pronouns, phoneNumber, 
        email, streetAddress, secondAddress, city, zipcode,
        country, stateProvince, drinkAlcohol, eatMeat, eatDairy,
        eatFish, eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions
    }, dispatch] = useReducer(reducer, initalState)

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
        <main className="card-stack">

            <Routes>
                <Route path="/" element={
                    <RSVPFormResponse rsvp={rsvp} dispatch={dispatch} />} />
                <Route path="/contact" element={
                    <RSVPFormContact firstName={firstName} lastName={lastName} 
                        pronouns={pronouns} phoneNumber={phoneNumber} 
                        email={email} streetAddress={streetAddress} secondAddress={secondAddress}
                        zipcode={zipcode} city={city} country={country} stateProvince={stateProvince} 
                        dispatch={dispatch} />} />
                <Route path="/dietary" element={
                    <RSVPFormDietary drinkAlcohol={drinkAlcohol} eatMeat={eatMeat} 
                        eatDairy={eatDairy} eatFish={eatFish} eatShellfish={eatShellfish}
                        eatEggs={eatEggs} eatGluten={eatGluten} eatPeanuts={eatPeanuts} 
                        moreRestrictions={moreRestrictions} dispatch={dispatch} />} />
                <Route path="/submit" element={
                    <RSVPFormSubmit rsvpCode={rsvpCode} contactString={contactString} 
                        firstName={firstName} lastName={lastName} rsvpString={rsvpString} 
                        dietaryString={dietaryString} dispatch={dispatch} />} />
            </Routes>

        </main>
    )
}