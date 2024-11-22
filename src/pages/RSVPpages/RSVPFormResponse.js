import React from 'react';
import { NavLink } from 'react-router-dom';
import '../../App.css';

export function RSVPFormResponse({rsvp, rsvpCode, dispatch}) {
    console.log(rsvp)
    console.log("code = ", rsvpCode)

    // const rsvpCodeLower = rsvpCode.lo

    return (
        <>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            
                <div class="rsvp">
                    <div id="main">
                        <h1>Repondez S'il Vous Plait!</h1>
                        <div>
                            <h2>May we expect your presence at our wedding on <br></br>
                                November 7th, 2025 in Brooklyn, NY?</h2>
                            <p>If need be, you can change this, but please let us know soon!</p>
                        </div>
                        {/* look at this maybe */}
                        <div id="rsvp-radio">
                            <div id="radio-item">
                                <input id="rsvp-yes" name="rsvp" type="radio"
                                    onClick={()=>dispatch({type: "rsvpInput", payload: "attending" })}></input>
                                <label className='radio-label' for="rsvp-yes">
                                    Yes, I will be in attendance!
                                </label>
                            </div>
                            <div id="radio-item">
                                <input id="rsvp-no" name="rsvp" type="radio"
                                    onClick={()=>dispatch({type: "rsvpInput", payload: "notattending" })}></input>
                                <label className='radio-label' for="rsvp-no">
                                    No, unfortunately I cannot attend
                                </label>
                            </div>
                        </div>
                        
                        { rsvpCode.toLowerCase() === 'def' 
                            ? <p>Are you bringing a plus one?
                              <br/> We will text you a unique link for your invitee.</p>
                            : ( rsvpCode.toLowerCase() === 'ghi'
                            ? <p>After the first guest fills out and submits this form, 
                              <br/>please continue to swipe for the next guest's form.</p> 
                            : <p>error</p> )}

                    </div>
                </div>

            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
                <span className='button-container'>
                    <NavLink className='btn-23' 
                        disabled={rsvp === 'undecided' ? true : false} 
                        to={rsvp === 'undecided' ? '/rsvp' : '/rsvp/contact'} 
                        end><marquee>Continue</marquee></NavLink>

                        {/* and there needs to be an error message too */}
                </span>
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        </>
    )
}