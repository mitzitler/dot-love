import React from 'react';
import { useState } from 'react';
// import { RSVPForm } from '../components/RSVPPage'
import { RSVPFormTop } from '../components/RSVPFormTop'
import { RSVPFormMiddle } from '../components/RSVPFormMiddle'
import { RSVPFormDiet } from '../components/RSVPFormDiet'
// import { RSVPFormSubmit } from '../components/RSVPFormSubmit'
import { count } from 'd3';
// this should contain both RSVP flows
// so it starts with a modal prompting either a log in or registration
// and then it contains either
//// starts the rsvp flow
//// logs in the user 
//// ????????

const RsvpOptions = Object.freeze({
    ATTENDING: "ATTENDING",
    NOT_ATTENDING: "NOT_ATTENDING",
    UNDECIDED: "UNDECIDED"
  });

export function RSVP() {

    const [rsvp, setRsvp] = useState(RsvpOptions.UNDECIDED);

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [pronouns, setPronouns] = useState("")
    const [phoneNumber, setPhoneNumber] = useState("");
    const [email, setEmail] = useState("");
    const [streetAddress, setStreetAddress] = useState('')
    const [secondAddress, setSecondAddress] = useState('')
    const [city, setCity] = useState('')
    const [zipcode, setZipcode] = useState('')
    const [country, setCountry] = useState('')
    const [stateProvince, setStateProvince] = useState('')

    const [drinkAlcohol, setDrinkAlcohol] = useState(true);
    const [eatMeat, setEatMeat] = useState(true);
    const [eatDairy, setEatDairy] = useState(true);
    const [eatFish, setEatFish] = useState(true)
    const [eatShellfish, setEatShellfish] = useState(true)
    const [eatEggs, setEatEggs] = useState(true)
    const [eatGluten, setEatGluten] = useState(true)
    const [eatPeanuts, setEatPeanuts] = useState(true)
    const [moreRestrictions, setMoreRestrictions] = useState('')

    console.log("alcohol:", drinkAlcohol, " zipcode: ", zipcode, firstName)

    return (
        <main>
            {/* can i do height: 80% ? */}
            <main className="section-content swipe-card w-full h-screen flex-grow bg-amber-400/75 border-amber-500/50 border-2">
                <RSVPFormTop rsvp={rsvp} setRsvp={setRsvp} RsvpOptions={RsvpOptions} />
            </main>
            <main className="section-content swipe-card w-full h-screen flex-grow bg-amber-400/75 border-amber-500/50 border-2">
                <RSVPFormMiddle
                firstName={firstName} setFirstName={setFirstName}
                lastName={lastName} setLastName={setLastName}
                pronouns={pronouns} setPronouns={setPronouns}
                phoneNumber={phoneNumber} setPhoneNumber={setPhoneNumber}
                email={email} setEmail={setEmail}
                streetAddress={streetAddress} setStreetAddress={setStreetAddress}
                secondAddress={secondAddress} setSecondAddress={setSecondAddress}
                zipcode={zipcode} setZipcode={setZipcode}
                city={city} setCity={setCity}
                country={country} setCountry={setCountry}
                stateProvince={stateProvince} setStateProvince={setStateProvince} />
            </main>
            <main className="section-content swipe-card w-full h-screen flex-grow bg-amber-400/75 border-amber-500/50 border-2">
                <RSVPFormDiet
                  drinkAlcohol={drinkAlcohol} setDrinkAlcohol={setDrinkAlcohol}
                  eatMeat={eatMeat} setEatMeat={setEatMeat}
                  eatDairy={eatDairy} setEatDairy={setEatDairy}
                  eatFish={eatFish} setEatFish={setEatFish}
                  eatShellfish={eatShellfish} setEatShellfish={setEatShellfish}
                  eatEggs={eatEggs} setEatEggs={setEatEggs}
                  eatGluten={eatGluten} setEatGluten={setEatGluten}
                  eatPeanuts={eatPeanuts} setEatPeanuts={setEatPeanuts}
                  moreRestrictions={moreRestrictions} setMoreRestrictions={setMoreRestrictions} />
            </main>
            {/* <main className="section-content swipe-card w-full h-screen flex-grow bg-amber-400/75 border-amber-500/50 border-2">
                <RSVPFormSubmit />
            </main> */}
        </main>
    )
}