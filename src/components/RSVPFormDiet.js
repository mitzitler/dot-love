import { useState } from "react";
import '../App.css';

// use gsap for fun red X animation and green CHECK animation

import "./dietary-restrictions/alcohol_1.png";
import "./dietary-restrictions/dairy.png";
import "./dietary-restrictions/eggs.png";
import "./dietary-restrictions/fish.png";
import "./dietary-restrictions/gluten.png";
import "./dietary-restrictions/meat.png";
import "./dietary-restrictions/peanuts.png";
import "./dietary-restrictions/alcohol_2.png";

const alcohol_yes = require("./dietary-restrictions/alcohol_1.png")
const dairy_yes = require("./dietary-restrictions/dairy.png")
const eggs_yes = require("./dietary-restrictions/eggs.png")
const fish_yes = require("./dietary-restrictions/fish.png")
const gluten_yes = require("./dietary-restrictions/gluten.png")
const meat_yes = require("./dietary-restrictions/meat.png")
const peanuts_yes = require("./dietary-restrictions/peanuts.png")
const other_yes = require("./dietary-restrictions/alcohol_2.png")

export function RSVPFormDiet({
  drinkAlcohol, setDrinkAlcohol,
  eatMeat, setEatMeat,
  eatDairy, setEatDairy,
  eatFish, setEatFish,
  eatShellfish, setEatShellfish,
  eatEggs, setEatEggs,
  eatGluten, setEatGluten,
  eatPeanuts, setEatPeanuts,
  moreRestrictions, setMoreRestrictions
}) {

  function handleDrinkAlcohol(drinkAlcohol) {setDrinkAlcohol(drinkAlcohol)} 
  function handleEatMeat(eatMeat) {setEatMeat(eatMeat)} 
  function handleEatDairy(eatDairy) {setEatDairy(eatDairy)} 
  function handleEatFish(eatFish) {setEatFish(eatFish)} 
  function handleEatShellfish(eatShellfish) {setEatShellfish(eatShellfish)} 
  function handleEatEggs(eatEggs) {setEatEggs(eatEggs)} 
  function handleEatGluten(eatGluten) {setEatGluten(eatGluten)} 
  function handleEatPeanuts(eatPeanuts) {setEatPeanuts(eatPeanuts)} 
  function handleMoreRestrictions(moreRestrictions) {setMoreRestrictions(moreRestrictions)} 

  return(
    <div class="rsvp">            
      <h2>... and any dietary restrictions, please!</h2> 
      <div className="m-auto pt-10 pb-0 grid grid-cols-4 gap-6 px-2">

          {/* gsap animate big red X on click */}

        <img src={alcohol_yes} alt="I drink alcohol" 
          className={drinkAlcohol ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleDrinkAlcohol(!drinkAlcohol)} /> 
          
        <img src={meat_yes} alt="I eat meat" 
          className={eatMeat ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleEatMeat(!eatMeat)}/>

        <img src={dairy_yes} alt="I eat dairy" 
          className={eatDairy ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleEatDairy(!eatDairy)}/>

        <img src={fish_yes} alt="I eat fish" 
          className={eatFish ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleEatFish(!eatFish)}/>  

        <img src={eggs_yes} alt="I eat eggs" 
          className={eatEggs ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleEatEggs(!eatEggs)}/>

        <img src={gluten_yes} alt="I eat gluten" 
          className={eatGluten ? "diet-image" : "diet-image-clicked"}
          onClick={()=>handleEatGluten(!eatGluten)}/>

        <img src={peanuts_yes} alt="I eat peanuts" 
            className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
            onClick={()=>handleEatPeanuts(!eatPeanuts)}/>

        {/* add in i eat shellfish for even 4x2 grid */}

        <img src={other_yes} alt="I have other restrictions" 
            // className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
            className="diet-image"
            // onClick={()=>handleEatPeanuts(!eatPeanuts)}
            />      
        </div>
      <div className="other-restrictions">
        <input label="other-restrictions" type="text" 
          id="other-restrictions" 
          placeholder="Other restrictions?" 
          value={moreRestrictions} 
          onInput={e=>handleMoreRestrictions(e.target.value)}></input>
        </div>
    </div>
)
}
