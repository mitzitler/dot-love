import '../../App.css';
import { NavLink, useLocation } from 'react-router-dom';
import React from 'react';
import { useState, useEffect, setShow } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { drinkAlcoholToggle, eatMeatToggle, eatDairyToggle, 
    eatFishToggle, eatEggsToggle, eatGlutenToggle, eatPeanutsToggle,
    eatShellfishToggle, moreRestrictionsInput} from '../../features/guest/rsvpSlice';
import { RedX } from   '../../components/RedX';
import { GreenO } from '../../components/GreenO';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter'

export function RSVPFormDietary({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {

    const [animation, setAnimation] = useState(null)
    const dispatch = useDispatch();

    const drinkAlcohol = useSelector((state) => state.rsvp.drinkAlcohol) 
    const eatMeat = useSelector((state) => state.rsvp.eatMeat)
    const eatDairy = useSelector((state) => state.rsvp.eatDairy)
    const eatFish = useSelector((state) => state.rsvp.eatFish)
    const eatShellfish = useSelector((state) => state.rsvp.eatShellfish)
    const eatEggs = useSelector((state) => state.rsvp.eatEggs)
    const eatGluten = useSelector((state) => state.rsvp.eatGluten)
    const eatPeanuts = useSelector((state) => state.rsvp.eatPeanuts)
    const moreRestrictions = useSelector((state) => state.rsvp.moreRestrictions)

    const handleClickAnimation = (event, toggleValue) => {
        const { id } = event.target;
        const position = { x: event.clientX - 40, y: event.clientY + 5 };

        setAnimation({ type: toggleValue ? 'green' : 'red', position });

        dispatch({ type: `${id}Toggle` });
    };

    const location = useLocation();
    useEffect(() => {
        window.scrollTo(0, 0); 
    }, [location.pathname]);

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>  
                    <h1 >... and any dietary restrictions, please!</h1> 
                    <h2>Touch the food icons to turn on and off your 
                        dietary restrictions</h2>
                    <div className="dietary-grid grid grid-cols-2">

                        {animation && animation.type === 'red' && (
                            <RedX
                                divPositionX={animation.position.x}
                                divPositionY={animation.position.y}
                                onAnimationEnd={() => setAnimation(null)}
                            />
                        )}
                        {animation && animation.type === 'green' && (
                            <GreenO
                                divPositionX={animation.position.x}
                                divPositionY={animation.position.y}
                                onAnimationEnd={() => setAnimation(null)}
                            />
                        )}

                      <img src="https://cdn.mitzimatthew.love/alcohol_1.png" id="alcohol" alt="I drink alcohol"
                        className={drinkAlcohol ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(drinkAlcoholToggle(e.target.value));
                            handleClickAnimation(e, !drinkAlcohol)}
                        }/> 

                      <img src="https://cdn.mitzimatthew.love/meat.png" id="meat" alt="I eat meat"
                        className={eatMeat ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatMeatToggle());
                            handleClickAnimation(e, !eatMeat)}
                        }/>

                      <img src="https://cdn.mitzimatthew.love/dairy.png" id="dairy" alt="I eat dairy"
                        className={eatDairy ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatDairyToggle());
                            handleClickAnimation(e, !eatDairy)}
                        }/>

                      <img src="https://cdn.mitzimatthew.love/fish.png" id="fish" alt="I eat fish"
                        className={eatFish ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatFishToggle());
                            handleClickAnimation(e, !eatFish)}
                        }/>  

                      <img src="https://cdn.mitzimatthew.love/eggs.png" id="eggs" alt="I eat eggs"
                        className={eatEggs ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatEggsToggle());
                            handleClickAnimation(e, !eatEggs)}
                        }/>

                      <img src="https://cdn.mitzimatthew.love/gluten.png" id="gluten" alt="I eat gluten"
                        className={eatGluten ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatGlutenToggle());
                            handleClickAnimation(e, !eatGluten)}
                        }/>

                      <img src="https://cdn.mitzimatthew.love/peanuts.png" id="peanuts" alt="I eat peanuts"
                        className={eatPeanuts ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatPeanutsToggle());
                            handleClickAnimation(e, !eatPeanuts)}
                        }/>

                      <img src="https://cdn.mitzimatthew.love/shellfish.png" id="shellfish" alt="I eat shellfish"
                        className={eatShellfish ? "diet-image" : "diet-image-clicked"}
                        onClick={(e)=>{
                            dispatch(eatShellfishToggle());
                            handleClickAnimation(e, !eatShellfish)}
                        }/>    

                    </div>
                    <div className="other-restrictions">
                        <input label="other-restrictions" type="text" 
                        id="other-restrictions" 
                        placeholder="Other restrictions?" 
                        // is this format right?
                        onChange={(e)=>dispatch(moreRestrictionsInput(e.target.value))}/> 
                    </div>
        </CardStackPage>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
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
