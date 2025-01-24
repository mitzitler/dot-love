import React from 'react';
import { NavLink } from 'react-router-dom';
import '../../App.css';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useDispatch, useSelector } from 'react-redux';
import { rsvpStatusInput } from '../../features/guest/rsvpSlice';

export function RSVPFormResponse({pageMainColor, pageSection, rsvpCode}) {

    const dispatch = useDispatch();

    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)
    const submitted = useSelector((state) => state.rsvp.submitted)

    return (
        <>
            <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
                { submitted === null ? <h1>Repondez S'il Vous Plait!</h1> : <h1>Please RSVP For the Second Guest...</h1> }
                <div>
                    <h2>May we expect your presence at our wedding on <br></br>
                        November 7th, 2025 in Brooklyn, NY?</h2>
                    <p>If need be, you can change this, but please let us know soon!</p>
                </div>
              {/* TODO: revisit this */}
                <div id="rsvp-radio">
                    <div id="radio-item">
                        <input id="rsvp-yes" name="rsvp" type="radio" value={rsvpStatus}
                            onClick={()=>dispatch(rsvpStatusInput("attending"))}></input>
                        <label className='radio-label' for="rsvp-yes">
                            Yes, I will be in attendance!
                        </label>
                    </div>
                    <div id="radio-item">
                        <input id="rsvp-no" name="rsvp" type="radio" value={rsvpStatus}
                            onClick={()=>dispatch(rsvpStatusInput("notattending"))}></input>
                        <label className='radio-label' for="rsvp-no">
                            No, unfortunately I cannot attend
                        </label>
                    </div>
                </div>
                
                { rsvpCode.toLowerCase() === 'def' 
                    ? <p>Are you bringing a plus one?
                        <br/> We will text you a unique link for your invitee.</p>
                    : ((rsvpCode.toLowerCase() === 'ghi' & submitted === null)
                    ? <p>After the first guest fills out and submits this form, 
                        <br/>please continue through the flow for the next guest's form.</p> 
                    : ((rsvpCode.toLowerCase() === 'ghi' & submitted != null)
                    ? <p>This RSVP will not be complete until both guests fill out the form. 
                        <br/>if you do not receive confirmation that the RSVPs were submitted, please start over!</p> 
                    : <p></p> ))}

            </CardStackPage>
            <CardStackFooter>
                <NavLink className='btn-23' 
                    disabled={rsvpStatus === 'undecided' ? true : false} 
                    to={rsvpStatus === 'undecided' ? '/rsvp' : '/rsvp/contact'} 
                    end><marquee>Continue</marquee></NavLink>
                    {/* and there needs to be an error message too */}
            </CardStackFooter>
        </>
    )
}
