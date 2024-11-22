import React from "react";
import { useState } from "react";

import "./dietary-restrictions/alcohol_1.png";
import "./dietary-restrictions/alcohol_1_no.png";
import "./dietary-restrictions/dairy.png";
import "./dietary-restrictions/dairy_no.png";
import "./dietary-restrictions/eggs.png";
import "./dietary-restrictions/eggs_no.png";
import "./dietary-restrictions/fish.png";
import"./dietary-restrictions/fish_no.png";
import "./dietary-restrictions/gluten.png";
import "./dietary-restrictions/gluten_no.png";
import "./dietary-restrictions/meat.png";
import "./dietary-restrictions/meat_no.png";
import "./dietary-restrictions/peanuts.png";
import "./dietary-restrictions/peanuts_no.png";
import "./dietary-restrictions/alcohol_2.png";
import "./dietary-restrictions/alcohol_2_no.png";

const alcohol_yes = require("./dietary-restrictions/alcohol_1.png")
const alcohol_no = require("./dietary-restrictions/alcohol_1_no.png")

const dairy_yes = require("./dietary-restrictions/dairy.png")
const dairy_no = require("./dietary-restrictions/dairy_no.png")

const eggs_yes = require("./dietary-restrictions/eggs.png")
const eggs_no = require("./dietary-restrictions/eggs_no.png")

const fish_yes = require("./dietary-restrictions/fish.png")
const fish_no = require("./dietary-restrictions/fish_no.png")

const gluten_yes = require("./dietary-restrictions/gluten.png")
const gluten_no = require("./dietary-restrictions/gluten_no.png")

const meat_yes = require("./dietary-restrictions/meat.png")
const meat_no = require("./dietary-restrictions/meat_no.png")

const peanuts_yes = require("./dietary-restrictions/peanuts.png")
const peanuts_no = require("./dietary-restrictions/peanuts_no.png")

const other_yes = require("./dietary-restrictions/alcohol_2.png")
const other_no = require("./dietary-restrictions/alcohol_2_no.png")

export function RSVPPageDietary({children}) {
    const [drinkAlcohol, setDrinkAlcohol] = useState(true);
    const [eatMeat, setEatMeat] = useState(true);
    const [eatDairy, setEatDairy] = useState(true);
    const [eatFish, setEatFish] = useState(true)
    const [eatEggs, setEatEggs] = useState(true)
    const [eatGluten, setEatGluten] = useState(true)
    const [eatPeanuts, setEatPeanuts] = useState(true)
    const [moreRestrictions, setMoreRestrictions] = useState('')

    function handleDrinkAlcohol(drinkAlcohol) {setDrinkAlcohol(drinkAlcohol)} 
    function handleEatMeat(eatMeat) {setEatMeat(eatMeat)} 
    function handleEatDairy(eatDairy) {setEatDairy(eatDairy)} 
    function handleEatFish(eatFish) {setEatFish(eatFish)} 
    function handleEatEggs(eatEggs) {setEatEggs(eatEggs)} 
    function handleEatGluten(eatGluten) {setEatGluten(eatGluten)} 
    function handleEatPeanuts(eatPeanuts) {setEatPeanuts(eatPeanuts)} 

    return(
        <div>            
            <h2 className="text-bold">... and any dietary restrictions, please!</h2> 
        {/*it would be cool if this section was actually a checkbox where you click stuff and it x's out like ghostbusters */} {/* wow I did it !*/}
            <div className="m-auto grid grid-cols-4 gap-2 px-2 py-2">
                <label className="swap swap-flip" id="alcohol">
                    <input type="checkbox"  id="alcohol" onChange={()=>handleDrinkAlcohol(!drinkAlcohol)} />
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={alcohol_yes} alt="I drink alcohol" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={alcohol_no} alt="I don't drink alcohol" />
                </label>
                <label className="swap swap-flip" id="meat" onChange={()=>handleEatMeat(!eatMeat)} >
                    <input type="checkbox"  id="meat"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={meat_yes} alt="I eat meat" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={meat_no} alt="I don't eat meat"/>
                </label>
                <label className="swap swap-rotate" id="dairy" onChange={()=>handleEatDairy(!eatDairy)} >
                    <input type="checkbox"  id="dairy"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={dairy_yes} alt="I eat dairy" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={dairy_no} alt="I don't eat dairy"/>
                </label>
                <label className="swap swap-rotate" id="fish" onChange={()=>handleEatFish(!eatFish)} >
                    <input type="checkbox"  id="fish"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={fish_yes} alt="I eat fish" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={fish_no} alt="I don't eat fish"/>
                </label>
                <label className="swap swap-rotate" id="eggs" onChange={()=>handleEatEggs(!eatEggs)} >
                    <input type="checkbox"  id="eggs"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={eggs_yes} alt="I eat eggs" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={eggs_no} alt="I don't eat eggs"/>
                </label>
                <label className="swap swap-rotate" id="gluten" onChange={()=>handleEatGluten(!eatGluten)} >
                    <input type="checkbox"  id="gluten"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={gluten_yes} alt="I eat gluten" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={gluten_no} alt="I don't eat gluten"/>
                </label>
                <label className="swap swap-rotate" id="peanuts" onChange={()=>handleEatPeanuts(!eatPeanuts)} >
                    <input type="checkbox"  id="peanuts"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={peanuts_yes} alt="I eat peanuts" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={peanuts_no} alt="I don't eat peanuts"/>
                </label>

                <label className="swap swap-rotate" id="other restrictions">
                    <input type="checkbox"  id="other restrictions"/>
                    <img className="swap-off h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={other_yes} alt="I have other restrictions" />
                    <img className="swap-on h-32 w-32 fill-current p-2" viewBox="0 0 32 32" src={other_no} alt="I don't have other restrictions"/>
                </label>
                {/* <ul> <input type="text" placeholder="Other restrictions"></input> </ul> */}
            </div>
        </div>
    )
}