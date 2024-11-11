import React from 'react';
import { NavLink } from 'react-router-dom';
import '../../App.css';

export function RSVPFormResponse({rsvp, dispatch}) {

    const guestType = 1.5

    return (
        <>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            
                <div class="rsvp">
                    <div id="main">
                        <h1>Repondez S'il Vous Plait!</h1>
                        <div>
                        <h2>
                            May we expect your presence at our wedding on <b>November 7th, 2025</b> in <b>Brooklyn, NY?</b>
                        </h2>
                        <p>
                            If need be, you can change this, but please let us know soon!
                        </p>
                        </div>
                        <div id="rsvp-radio">
                            <div id="radio-item">
                            <input id="rsvp-yes" name="rsvp" type="radio"
                            value={rsvp} 
                            onClick={()=>dispatch({type: "rsvpInput", payload: "attending" })}></input>
                            <label for="rsvp-yes">
                                I will be in attendance
                            </label>
                            </div>
                            <div id="radio-item">
                            <input id="rsvp-no" name="rsvp" type="radio"
                            value={rsvp} 
                            onClick={()=>dispatch({type: "rsvpInput", payload: "notattending" })}></input>
                            <label for="rsvp-no">
                                Unfortunately I cannot attend
                            </label>
                            </div>
                        </div>
                        <h2> Please swipe or use the arrow keys to continue through this form! </h2>

                        { guestType === 1.5 
                            ? <p><b>Are you bringing a plus one?</b> We will text you a unique link for your invitee.</p>
                            : ( guestType === 2.0 
                            ? <p>After the first guest fills out and submits this form, <b>please continue to swipe for the next guest's form.</b></p> 
                            : <></> )}
                        <span>
                            <NavLink className='next-btn' to='/contact' end>Continue...</NavLink> 
                        </span>

                    </div>
                </div>

            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        </>
    )
}