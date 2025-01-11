import '../../App.css';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useDispatch, useSelector } from 'react-redux';
import { submitFormGC1, submitFormGC1_5, submitFormGC2 } from '../../features/guest/rsvpSlice';

// on desktop all the information is pushed down too far

export function RSVPFormSubmit({pageMainColor, pageSection}) {

    const dispatch = useDispatch();

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode)
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)

    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const phoneNumber = useSelector((state) => state.rsvp.phoneNumber)
    const email = useSelector((state) => state.rsvp.email)
    const streetAddress = useSelector((state) => state.rsvp.streetAddress)
    const secondAddress = useSelector((state) => state.rsvp.secondAddress)
    const city = useSelector((state) => state.rsvp.city)
    const zipcode = useSelector((state) => state.rsvp.zipcode)
    const country = useSelector((state) => state.rsvp.country)
    const stateProvince = useSelector((state) => state.rsvp.stateProvince)

    const drinkAlcohol = useSelector((state) => state.rsvp.drinkAlcohol) 
    const eatMeat = useSelector((state) => state.rsvp.eatMeat)
    const eatDairy = useSelector((state) => state.rsvp.eatDairy)
    const eatFish = useSelector((state) => state.rsvp.eatFish)
    const eatShellfish = useSelector((state) => state.rsvp.eatShellfish)
    const eatEggs = useSelector((state) => state.rsvp.eatEggs)
    const eatGluten = useSelector((state) => state.rsvp.eatGluten)
    const eatPeanuts = useSelector((state) => state.rsvp.eatPeanuts)
    const moreRestrictions = useSelector((state) => state.rsvp.moreRestrictions)

    const rsvpSubmission = useSelector((state) => state.rsvp.rsvpSubmission)

    const name = firstName + " " + lastName

    const rsvpString = rsvpStatus === "attending" ? "We are excited you are coming!" :
        "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    const contactString = "Hi " + firstName + " " + lastName + " (" + pronouns + "), " +
        "we can reach you at " + phoneNumber + " or " + email + " and your mailing address is " + 
        streetAddress + " " + secondAddress + ", in " + city + ", " + zipcode + " - " + 
        stateProvince + ", " + country 

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

    // const rsvpCode = "DEF"

    const [clicked, setClicked] = useState(false)

    function handleClicked() {
        setClicked(!clicked);
        console.log(clicked)
    }

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
            <h1 id="submit-header1">Does this all look right, {name}?</h1>
            <p id="submit-header2">({pronouns})</p>
            <p>{rsvpString}</p>
            <div className="submit-div grid grid-cols-2">
                <div className="submit-card-left">
                    {/* i hate this styling so much */}
                    <h3 className="submit-text-overlay ">
                    Your mailing address is: {streetAddress} {city}, {stateProvince} {zipcode} - in  {countryNew}
                    </h3>
                    <p></p>
                    <h3 className="submit-text-overlay">
                    We will reach out to you at {phoneNumber} and {email}
                    </h3>
                </div>
                {/* need to make much smaller bottom padding */}
                <div className="submit-card-right">
                    <h3 className="submit-text-overlay">
                        {createRestrictionsString(dietaryRestrictions)}
                    </h3>
                    <p></p>
                    <h3 className="submit-text-overlay">
                        {createInclusionsString(dietaryInclusions)}
                    </h3>
                    {moreRestrictions.length > 0 && 
                    <>
                        <p></p>
                        <h3 className="submit-text-overlay">
                            You also noted restrictions: {moreRestrictions}
                        </h3>
                    </>
                    }
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
        </CardStackPage>
        <CardStackFooter>
            <NavLink className='btn-23' to='/rsvp/dietary' end><marquee>Return</marquee></NavLink> 
            {rsvpCode.toUpperCase() === 'ABC'
            ? <button className='btn-23' onClick={()=>
                {dispatch(submitFormGC1(`${firstName}_${lastName}`));
                console.log(rsvpSubmission)}
            }><marquee>Submit</marquee></button>
            : rsvpCode.toUpperCase() === 'DEF'
            ? <button className='btn-23' onClick={()=>dispatch(submitFormGC1_5(`${firstName}_${lastName}`))}><marquee>Submit</marquee></button>
            : rsvpCode.toUpperCase() === 'GHI'
            ? <NavLink className='btn-23' to='/rsvp' onClick={()=>dispatch(submitFormGC2(`${firstName}_${lastName}`))}><marquee>Submit</marquee></NavLink>
            : <p>error you should not have gotten this far!!</p>
            }
        </CardStackFooter>
    </>
    )
}

// {
//     "registration_fields": {
//         "first_last": "mitzi_zitler"
//         "rsvpStatus": "ATTENDING",
//         "pronouns": "SHEHER",
//         "streetAddress": "221 s 3rd st",
//         "secondAddress": "5b",
//         "city": "brooklyn",
//         "country": "united states",
//         "stateProvince": "new york",
//         "phone": "+15046387943",
//         "email": "mitzitler@gmail.com",
//         "drinkAlcohol": true,
//         "eatMeat": true,
//         "eatDairy": true,
//         "eatFish": true,
//         "eatShellfish": true,
//         "eatEggs": true,
//         "eatGluten": true,
//         "eatPeanuts": true,
//         "moreRestrictions": "",
//         "pair_first_last": "",
//         "rsvpCode": "GHI",
//         "zipcode": "11211",
//         "hasPlusOne": false
//     },
//     "referralCode": ""
// }