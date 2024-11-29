import '../../App.css';
import { NavLink } from 'react-router-dom';
import React from 'react';
import { useState } from 'react';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';


// use gsap for fun red X animation and green CHECK animation

import "../../assets/dietary-restrictions/alcohol_1.png" 
import "../../assets/dietary-restrictions/dairy.png";
import "../../assets/dietary-restrictions/eggs.png";
import "../../assets/dietary-restrictions/fish.png";
import "../../assets/dietary-restrictions/gluten.png";
import "../../assets/dietary-restrictions/meat.png";
import "../../assets/dietary-restrictions/peanuts.png";
import "../../assets/dietary-restrictions/shellfish.png";


const Alcohol = require("../../assets/dietary-restrictions/alcohol_1.png")
const Dairy = require("../../assets/dietary-restrictions/dairy.png")
const Eggs = require("../../assets/dietary-restrictions/eggs.png")
const Fish = require("../../assets/dietary-restrictions/fish.png")
const Gluten = require("../../assets/dietary-restrictions/gluten.png")
const Meat = require("../../assets/dietary-restrictions/meat.png")
const Peanuts = require("../../assets/dietary-restrictions/peanuts.png")
const Shellfish = require("../../assets/dietary-restrictions/shellfish.png")

export function RSVPFormDietary({pageMainColor, pageSection, drinkAlcohol, eatMeat, eatDairy, eatFish, 
  eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions, dispatch}) {

  const [divPositiion, setDivPosition] = useState({ x: 0, y: 0 })

  function handleClickAnimation(event) {
    console.log("x: ", event.clientX, " - y: ", event.clientY)
    setDivPosition({ x: event.clientX, y: event.clientY})
    // document.body.textContent =
    // "clientX: " + event.clientX +
    // " - clientY: " + event.clientY;
    // ?? // https://stackoverflow.com/questions/53337998/insert-html-at-clientx-and-clienty-position-of-cursor-in-editor-having-div-conte
  }

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>  
                    <h1 >... and any dietary restrictions, please!</h1> 
                    <h2 class="px-5 py-0 my-0">Touch the food icons to turn on and off your 
                        dietary restrictions</h2>
                    <div className="dietary-grid grid grid-cols-2">

                        {/* gsap animate big red X on click */}

                        {/* <div onClick={handleClickAnimation}> */}
                            <div className='big-red-x'
                                style ={{
                                    position: 'absolute',
                                    left: divPositiion.x-60,
                                    top: divPositiion.y-60
                                }}
                            >
                                X
                            </div>
                        {/* </div> */}

                        <img src={Alcohol} alt="I drink alcohol" 
                        className={drinkAlcohol ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "drinkAlcoholToggle"});
                            handleClickAnimation(e)}
                        }/> 
                        
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

                        <img src={Shellfish} alt="I eat shellfish" 
                        className={eatShellfish ? "diet-image" : "diet-image-clicked"}
                        onClick={()=>dispatch({type: "eatShellfishToggle"})}/>    

                    </div>
                    <div className="other-restrictions">
                        <input label="other-restrictions" type="text" 
                        id="other-restrictions" 
                        placeholder="Other restrictions?" 
                        onChange={(e)=>dispatch({type: "moreRestrictionsInput", payload: e.target.value})}/>
                    </div>
        </CardStackPage>
        <CardStackFooter>
                <NavLink className='btn-23' to='/rsvp/contact' end>
                    <marquee>Return</marquee>
                </NavLink> 
                {/* disable this for the first 5 seconds after render */}
                <NavLink className='btn-23' to='/rsvp/submit' end>
                    <marquee>Continue</marquee>
                </NavLink> 
        </CardStackFooter>
    </>
    )
}