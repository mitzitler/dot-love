import '../../App.css';
import { NavLink } from 'react-router-dom';

export function RSVPFormSubmit({rsvpCode, 
    // contactString, dietaryString, 
    // firstName, lastName, pronouns,
    // phoneNumber,email, streetAddress, secondAddress, zipcode, city, country, stateProvince, 
    dispatch}) {

    const firstName = "Pritham"
    const lastName = "Swaminathan"
    const pronouns = "he/him"
    const phoneNumber = "352 352 3522"
    const email = "pritham@pritham.com"
    const streetAddress = "221 S 3rd St"
    const secondAddress = "6A"
    const zipcode = "11211"
    const city = "Brooklyn"
    const country = "United States"
    const stateProvince = "New York"


    const drinkAlcohol = false 
    const eatMeat = false
    const eatDairy = false
    const eatFish = false
    const eatShellfish = false 
    const eatEggs = false
    const eatGluten = true
    const eatPeanuts = true 
    const moreRestrictions = ""

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

  return(
    <>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            <div class="rsvp">    

            <h1 class="pt-20">Does this all look right?</h1> 
            <div className="grid col-2">
                <h2>Hi {firstName} {lastName}, ({pronouns})</h2>
                
                <div className="mx-auto mt-0 grid grid-cols-2 px-2">
                    <div>
                        <div className="submit-card bg-rose-400/75 border-rose-400/75 border-2 backdrop-blur-md">
                            {/* i hate this styling so much */}
                            <h3 className="submit-text-overlay ">
                            Your mailing address is: {streetAddress} {city}, {stateProvince} {zipcode} - in  {country}
                            </h3>
                            <p></p>
                            <h3 className="submit-text-overlay">
                            We will reach out to you at {phoneNumber} and {email}
                            </h3>
                        </div>
                    </div>
                    <div>
                        <div className="submit-card bg-indigo-400/75 border-indigo-400/75 border-2 backdrop-blur-md">
                            <h3 className="submit-text-overlay">
                                {createRestrictionsString(dietaryRestrictions)}
                            </h3>
                            <p></p>
                            <h3 className="submit-text-overlay">
                                {createInclusionsString(dietaryInclusions)}
                            </h3>
                        </div>
                    
                
                {/* <p className='p-5'>{contactString}</p> */}
                {/* <p className='p-5'>{dietaryString}</p> */}
            </div>
            
            {/* if guest code is 1.5, then quick radio for are you taking a guest or not
            when they submit, they will be texted the guest code */}
            {}
            </div>
            </div>
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