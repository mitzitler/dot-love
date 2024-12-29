import '../../App.css';
import { NavLink } from 'react-router-dom';
import React from 'react';
import { useState, useEffect, setShow } from 'react';
import { RedX } from   '../../components/RedX';
import { GreenO } from '../../components/GreenO';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter'

import "../../assets/dietary-restrictions/alcohol_1.png" 
import "../../assets/dietary-restrictions/dairy.png";
import "../../assets/dietary-restrictions/eggs.png";
import "../../assets/dietary-restrictions/fish.png";
import "../../assets/dietary-restrictions/gluten.png";
import "../../assets/dietary-restrictions/meat.png";
import "../../assets/dietary-restrictions/peanuts.png";
import "../../assets/dietary-restrictions/shellfish.png";
import { click } from '@testing-library/user-event/dist/click';


const Alcohol = require("../../assets/dietary-restrictions/alcohol_1.png")
const Dairy = require("../../assets/dietary-restrictions/dairy.png")
const Eggs = require("../../assets/dietary-restrictions/eggs.png")
const Fish = require("../../assets/dietary-restrictions/fish.png")
const Gluten = require("../../assets/dietary-restrictions/gluten.png")
const Meat = require("../../assets/dietary-restrictions/meat.png")
const Peanuts = require("../../assets/dietary-restrictions/peanuts.png")
const Shellfish = require("../../assets/dietary-restrictions/shellfish.png")

// const click_counter = {
//     alcohol: 0,
//     dairy: 0,
//     eggs: 0,
//     fish: 0,
//     gluten: 0,
//     meat: 0,
//     peanuts: 0,
//     shellfish: 0
// }

export function RSVPFormDietary({pageMainColor, pageSection, drinkAlcohol, eatMeat, eatDairy, eatFish, 
  eatShellfish, eatEggs, eatGluten, eatPeanuts, moreRestrictions, dispatch}) {

  const [divSymbol, setDivSymbol] = useState(true)
  const [divPositiion, setDivPosition] = useState({ x: 0, y: 0 })
  const [counter, setCounter] = useState(0)
  const [clickCounter, setClickCounter] = useState({
    alcohol: 0,
    dairy: 0,
    eggs: 0,
    fish: 0,
    gluten: 0,
    meat: 0,
    peanuts: 0,
    shellfish: 0,
  });

  console.log("count is ", counter)
  let newCounter = 0

  function handleClickAnimation(event) {
    console.log("Click position: x: ", event.clientX, ", y: ", event.clientY)
    console.log(event.target.id)
    setDivPosition({ x: event.clientX - 40, y: event.clientY + 5})
    setClickCounter((prevState) => ({
        ...prevState,
        [event.target.id]: prevState[event.target.id] + 1,
    }))
    if ( counter == NaN ) { newCounter = 0;} 
    else { newCounter = counter;}
    setCounter(newCounter + 1)
    // document.body.textContent =
    // "clientX: " + event.clientX +
    // " - clientY: " + event.clientY;
    // ?? // https://stackoverflow.com/questions/53337998/insert-html-at-clientx-and-clienty-position-of-cursor-in-editor-having-div-conte
    // console.log("click counter is: ", [event.target.id], ": ", {clickCounter[event.target.id]})
}

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>  
                    <h1 >... and any dietary restrictions, please!</h1> 
                    <h2 class="px-5 py-0 my-0">Touch the food icons to turn on and off your 
                        dietary restrictions</h2>
                    <div className="dietary-grid grid grid-cols-2">

                        {/* gsap animate big red X on click */}
                        {counter > 0 && <RedX divPositiionX={divPositiion.x} divPositiionY={divPositiion.y}/>}
                        {counter > 0 && <GreenO divPositiionX={divPositiion.x} divPositiionY={divPositiion.y}/>}
                        {/* <RedX divPositiionX={divPositiion.x} divPositiionY={divPositiion.y}/> */}

                            {/* <div className='big-red-x'
                                style ={{
                                    position: 'absolute',
                                    left: divPositiion.x,
                                    top: divPositiion.y,
                                    margin: 'auto',
                                    textAlign: 'center',
                                    justifyContent: 'center',
                                    
                                }}
                            >
                                ❌
                            </div> */}
                            
                        {/* </div> */}

                        <img src={Alcohol} id="alcohol" alt="I drink alcohol" 
                        className={drinkAlcohol ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "drinkAlcoholToggle"});
                            setCounter();
                            handleClickAnimation(e)}
                        }/> 
                            {/* <div class="redx-onclick position-absolute">❌</div> */}
                            {/* <div>🚫</div> */}
                        
                        <img src={Meat} id="meat" alt="I eat meat" 
                        className={eatMeat ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatMeatToggle"});
                            handleClickAnimation(e)}
                        }/>

                        <img src={Dairy} id="dairy" alt="I eat dairy" 
                        className={eatDairy ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatDairyToggle"});
                            handleClickAnimation(e)}
                        }/>

                        <img src={Fish} id="fish" alt="I eat fish" 
                        className={eatFish ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatFishToggle"});
                            handleClickAnimation(e)}
                        }/>  

                        <img src={Eggs} id="eggs" alt="I eat eggs" 
                        className={eatEggs ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatEggsToggle"});
                            handleClickAnimation(e)}
                        }/>

                        <img src={Gluten} id="gluten" alt="I eat gluten" 
                        className={eatGluten ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatGlutenToggle"});
                            handleClickAnimation(e)}
                        }/>

                        <img src={Peanuts} id="peanuts" alt="I eat peanuts" 
                        className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatPeanutsToggle"});
                            handleClickAnimation(e)}
                        }/>

                        <img src={Shellfish} id="shellfish" alt="I eat shellfish" 
                        className={eatShellfish ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{dispatch({type: "eatShellfishToggle"});
                            handleClickAnimation(e)}
                        }/>    

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