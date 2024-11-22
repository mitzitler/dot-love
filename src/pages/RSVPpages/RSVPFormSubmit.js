import '../../App.css';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';

export function RSVPFormSubmit({ // rsvpCode, 
    contactString, dietaryString, 
    firstName, lastName, pronouns,
    phoneNumber,email, streetAddress, secondAddress, zipcode, city, country, stateProvince, 
    drinkAlcohol, eatMeat, eatDairy, eatFish, eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions,
    dispatch}) {

    const countryNew = country === "United States" ? "the US" : country

    const dietaryDict = {
        drinkAlcohol: "drink alcohol",
        eatMeat: "eat meat", 
        eatDairy: "have dairy", 
        eatFish: "eat fish", 
        eatShellfish: "eat shellfish", 
        eatEggs: "eat eggs", 
        eatGluten: "have gluten", 
        eatPeanuts: "eat peanuts", 
        // moreRestrictions: "?????"
    }
    
    let dietaryInclusions = []
    let dietaryRestrictions = []

    for (const [key, value] of Object.entries(dietaryDict)) {
        if (eval(key)) {
            dietaryInclusions.push(value)
        } else {
            dietaryRestrictions.push(value)
        }
    }

    function createRestrictionsString(res) {
        if (res.length === 0) {return "You don't have any dietary restrictions."}
        if (res.length === 1) {return `You can't ${res[0]}.`}
        if (res.length === 8) {return "You can't have any of these allergens or restrictions"}

        const allButLast = res.slice(0, -1).join(', ');
        const lastItem = res[res.length - 1];

        return `You can't ${allButLast} or ${lastItem}.`;
    }

    function createInclusionsString(inc) {
        if (inc.length === 0) {return "You do eat whatever else is left?"}
        if (inc.length === 1) {return `You only ${inc[0]}.`}
        if (inc.lenght === 8 & moreRestrictions === "") {return "You don't have any dietary restrictions! Feel free to return to the previous page if this is incorrect"}
        if (inc.lenght === 8 & moreRestrictions !== "") {return "You wrote in your restriction(s): " + moreRestrictions}

        const allButLast = inc.slice(0, -1).join(', ');
        const lastItem = inc[inc.length - 1];
        
        return `You can ${allButLast} and ${lastItem}.`;
    }

    const rsvpCode = "DEF"

    const [clicked, setClicked] = useState(false)

    function handleClicked() {
        setClicked(!clicked);
        console.log(clicked)
    }

  return(
    <>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            <div class="rsvp">    

            <h1 id="submit-header1">Does this all look right, {firstName} {lastName}?</h1>
            <p id="submit-header2">({pronouns})</p>
            <div className="grid col-2">
                
                <div className="submit-div mx-auto my-0 grid grid-cols-2 px-2">
                    <div>
                        <div className="submit-card-left"
                        // className="submit-card bg-rose-400/75 border-rose-400/75 border-2 
                        // backdrop-blur-md"
                        >
                            {/* i hate this styling so much */}
                            <h3 className="submit-text-overlay ">
                            Your mailing address is: {streetAddress} {city}, {stateProvince} {zipcode} - in  {countryNew}
                            </h3>
                            <p></p>
                            <h3 className="submit-text-overlay">
                            We will reach out to you at {phoneNumber} and {email}
                            </h3>
                        </div>
                    </div>
                    <div>
                        <div className="submit-card-right">
                            <h3 className="submit-text-overlay">
                                {createRestrictionsString(dietaryRestrictions)}
                            </h3>
                            <p></p>
                            <h3 className="submit-text-overlay">
                                {createInclusionsString(dietaryInclusions)}
                            </h3>
                        </div>

                    </div>
                </div>

            </div>
            
            {rsvpCode === 'DEF' 
            ? 
            <div class="conditional-plusone">
                <h2>Are you planning on bringing a guest?</h2>
                <div>
                {/* class="grid grid-cols-8"> */}
                    {/* <p 
                    className={!clicked ? "col-span-1" :
                    "conditional-checked col-span-1"}
                    onClick={()=>handleClicked()}
                    ></p> */}

                    <label className='checkbox-guest' for="guest-yes">
                        Check this box to be texted a unique link for your guest to RSVP. This link will be active until August 7th, 2024 - three months before the wedding.
                        <input id="guest-yes" name="guest-yes" type="checkbox"
                            onClick={()=>handleClicked()}/>
                        <span class="checkmark"></span>
                    </label>
                </div>
            </div>
            :<></>}
            </div>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
            <span className='button-container'>
                <NavLink className='btn-23' to='/rsvp/dietary' end><marquee>Return</marquee></NavLink> 
                {rsvpCode.toUpperCase() === 'ABC'
                ? <button className='btn-23' onClick={()=>dispatch({type:"submitFormGC1", payload:`${firstName} ${lastName}`})}><marquee>Submit</marquee></button>
                : rsvpCode.toUpperCase() === 'DEF'
                ? <button className='btn-23' onClick={()=>dispatch({type:"submitFormGC1.5", payload:`${firstName} ${lastName}`})}><marquee>Submit</marquee></button>
                : rsvpCode.toUpperCase() === 'GHI'
                ? <NavLink className='btn-23' to='/rsvp' onClick={()=>dispatch({type:"submitFormGC2", payload:`${firstName} ${lastName}`})}><marquee>Submit</marquee></NavLink>
                : <p>error you should not have gotten this far!!</p>
                }
                
            </span>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        {/* <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/> */}
    </>
    )
}