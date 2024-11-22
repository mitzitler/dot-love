import React from 'react';
import { useState } from 'react';
import { Draggable } from 'gsap/all';
// import { RSVPForm } from '../components/RSVPPage'
import { RSVPFormTop } from '../components/RSVPFormTop'
import { RSVPFormMiddle } from '../components/RSVPFormMiddle'
import { RSVPFormDiet } from '../components/RSVPFormDiet'
// import { RSVPFormSubmit } from '../components/RSVPFormSubmit'
// import { count } from 'd3';
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

    // draggable to trigger swipe animation? https://gsap.com/community/forums/topic/18846-swipe-cards-using-greensock/
    // var lastX = 0;
    // var direction;
    // var animDirection;
    // Draggable.create(document.createElement("section"), {
    // trigger: "#swipe-card",
    // type: "x",
    // minimumMovement: 10,
    // onDragStart: function() {
    //     if (inAnimation && inAnimation.isActive()) {
    //     // inAnimation.timeScale(10);
    //     // outAnimation.timeScale(10);
    //     TweenMax.to([inAnimation, outAnimation], 0.3, {timeScale: 10})
        
    //     if (this.getDirection() === "left") {
    //         nextSlide = slides[currentSlide.index - 1] || slides[slides.length - 1];
    //     } else {
    //         nextSlide = slides[currentSlide.index + 1] || slides[0];
    //     }
    //     } else if (this.getDirection() === "left") {
    //     setSlide(slides[currentSlide.index - 1] || slides[slides.length - 1]);
    //     } else {
    //     setSlide(slides[currentSlide.index + 1] || slides[0]);
    //     }
    // }
    // });


    // var inAnimation = null;
    // var outAnimation = null;
    // var nextSlide = null;

    return (
        <main className="card-stack" >
            {/* can i do height: 80% ? */}
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
                <RSVPFormTop rsvp={rsvp} setRsvp={setRsvp} RsvpOptions={RsvpOptions} />
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
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
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
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
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
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
            </section>
            {/* <section className="section-content swipe-card w-full h-screen flex-grow bg-amber-400/75 border-amber-500/50 border-2">
                <RSVPFormSubmit />
            </section> */}
        </main>
    )
}