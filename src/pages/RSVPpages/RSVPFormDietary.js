import '../../App.css';
import { NavLink } from 'react-router-dom';


// use gsap for fun red X animation and green CHECK animation

import "../../assets/dietary-restrictions/alcohol_1.png" 
import "../../assets/dietary-restrictions/dairy.png";
import "../../assets/dietary-restrictions/eggs.png";
import "../../assets/dietary-restrictions/fish.png";
import "../../assets/dietary-restrictions/gluten.png";
import "../../assets/dietary-restrictions/meat.png";
import "../../assets/dietary-restrictions/peanuts.png";
import "../../assets/dietary-restrictions/alcohol_2.png";


const Alcohol = require("../../assets/dietary-restrictions/alcohol_1.png")
const Dairy = require("../../assets/dietary-restrictions/dairy.png")
const Eggs = require("../../assets/dietary-restrictions/eggs.png")
const Fish = require("../../assets/dietary-restrictions/fish.png")
const Gluten = require("../../assets/dietary-restrictions/gluten.png")
const Meat = require("../../assets/dietary-restrictions/meat.png")
const Peanuts = require("../../assets/dietary-restrictions/peanuts.png")
const Other = require("../../assets/dietary-restrictions/alcohol_2.png")

export function RSVPFormDietary({drinkAlcohol, eatMeat, eatDairy, eatFish, 
  eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions, dispatch}) {

  return(
    <>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            <div class="rsvp">            
                <h1 class="pt-10 my-0">... and any dietary restrictions, please!</h1> 
                <h2 class="px-5 py-0 my-0">Touch the food icons to turn on and off your 
                    dietary restrictions</h2>
                <div className="mx-auto mt-0 grid grid-cols-2 px-2">

                    {/* gsap animate big red X on click */}

                    <img src={Alcohol} alt="I drink alcohol" 
                    className={drinkAlcohol ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "drinkAlcoholToggle"})}/> 
                    
                    <img src={Meat} alt="I eat meat" 
                    className={eatMeat ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatMeatToggle"})}/>

                    <img src={Dairy} alt="I eat dairy" 
                    className={eatDairy ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatDairyToggle"})}/>

                    <img src={Fish} alt="I eat fish" 
                    className={eatFish ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatFishToggle"})}/>  

                    <img src={Eggs} alt="I eat eggs" 
                    className={eatEggs ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatEggsToggle"})}/>

                    <img src={Gluten} alt="I eat gluten" 
                    className={eatGluten ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatGlutenToggle"})}/>

                    <img src={Peanuts} alt="I eat peanuts" 
                    className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
                    onClick={()=>dispatch({type: "eatPeanutsToggle"})}/>

                    {/* add in i eat shellfish for even 4x2 grid */}

                    <img src={Other} alt="I eat shellfish" 
                    // className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
                    className="diet-image"
                    // onClick={()=>dispatch({type: "eatShellfishToggle"})}
                    />      
                    </div>
                <div className="other-restrictions">
                    <input label="other-restrictions" type="text" 
                    id="other-restrictions" 
                    placeholder="Other restrictions?" 
                    onChange={(e)=>dispatch({type: "moreRestrictionsInput", payload: e.target.value})}/>
                </div>

            </div>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
            <span className='button-container'>
                <NavLink className='btn-23' to='/rsvp/contact' end>
                    <marquee>Return</marquee>
                </NavLink> 
                {/* disable this for the first 5 seconds after render */}
                <NavLink className='btn-23' to='/rsvp/submit' end>
                    <marquee>Continue</marquee>
                </NavLink> 
            </span>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        {/* <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/> */}
    </>
    )
}