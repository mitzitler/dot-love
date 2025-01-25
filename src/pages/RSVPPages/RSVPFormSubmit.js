import '../../App.css';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { FormSubmitLeft } from '../../components/FormSubmitLeft.js';
import { FormSubmitRight } from '../../components/FormSubmitRight.js';
import { useDispatch, useSelector } from 'react-redux';
import { submitFormGC1, submitFormGC1_5, submitFormGC2 } from '../../features/guest/rsvpSlice';
import { storeCompletedRSVP } from '../../features/guest/rsvpCompletedSlice.js'

// on desktop all the information is pushed down too far

export function RSVPFormSubmit({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {

    const dispatch = useDispatch();

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode)
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)
    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const submitted = useSelector((state) => state.rsvp.submitted)
    const rsvpSubmission = useSelector((state) => state.rsvp.rsvpSubmission)
    const fullGuestInfo = useSelector((state) => state.rsvp)

    console.log(fullGuestInfo)

    const name = firstName + " " + lastName

    const rsvpString = rsvpStatus === "attending" ? "We are excited you are coming!" :
        "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    const [dateLinkRequested, setDateLinkRequested] = useState(false)

    function handleDateLinkRequested() {
        setDateLinkRequested(!dateLinkRequested);
        console.log('text me a link: ' + !dateLinkRequested)
    }

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
            <h1 id="submit-header1">Does this all look right, {name}?</h1>
            <p id="submit-header2">({pronouns})</p>
            <p>{rsvpString}</p>
            <div className="submit-div grid grid-cols-2">
                <FormSubmitLeft />
                {/* need to make much smaller bottom padding */}
                <FormSubmitRight />
            </div>
            
            {/* conditional case for open plus ones */}
            {rsvpCode.toUpperCase() === 'DEF' 
            ? 
            <div class="conditional-plusone">
                <h2>Are you planning on bringing a guest?</h2>
                <div>
                    <label className='checkbox-guest' for="guest-yes">
                        Check this box to be sent a unique link for your guest to RSVP. This link will be active until August 7th, 2024 - three months before the wedding.
                        <input id="guest-yes" name="guest-yes" type="checkbox"
                            onClick={()=>handleDateLinkRequested()}/>
                        <span class="checkmark"></span>
                    </label>
                </div>
            </div>
            :<></>}

        </CardStackPage>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor}>
            <NavLink className='btn-23' to='/rsvp/dietary' end><marquee>Return</marquee></NavLink> 

            {rsvpCode.toUpperCase() === 'ABC'
            ? <NavLink className='btn-23' to='/rsvp/confirmation' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Submit</marquee></NavLink>

            : rsvpCode.toUpperCase() === 'DEF'
            ? <NavLink className='btn-23' to='/rsvp/confirmation' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Submit</marquee></NavLink>
            
            : (rsvpCode.toUpperCase() === 'GHI' & submitted === null)
            ? <NavLink className='btn-23' to='/rsvp' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Continue</marquee></NavLink>
            
            : (rsvpCode.toUpperCase() === 'GHI' & submitted != null)
            ? <NavLink className='btn-23' to='/rsvp/confirmation' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Submit</marquee></NavLink>
            
            : <p>error you should not have gotten this far!!</p>}

        </CardStackFooter>
    </>
    )
}