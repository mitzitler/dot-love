import '../App.css';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

export function FormSubmitRight() {

    const drinkAlcohol = useSelector((state) => state.rsvp.drinkAlcohol) 
    const eatMeat = useSelector((state) => state.rsvp.eatMeat)
    const eatDairy = useSelector((state) => state.rsvp.eatDairy)
    const eatFish = useSelector((state) => state.rsvp.eatFish)
    const eatShellfish = useSelector((state) => state.rsvp.eatShellfish)
    const eatEggs = useSelector((state) => state.rsvp.eatEggs)
    const eatGluten = useSelector((state) => state.rsvp.eatGluten)
    const eatPeanuts = useSelector((state) => state.rsvp.eatPeanuts)
    const moreRestrictions = useSelector((state) => state.rsvp.moreRestrictions)

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
    )

}