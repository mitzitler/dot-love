import '../../App.css';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { CardStackPageClass } from '../../components/CardStackPageClass';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { FormSubmitLeft } from '../../components/FormSubmitLeft.js';
import { FormSubmitRight } from '../../components/FormSubmitRight.js';
import { useDispatch, useSelector } from 'react-redux';
import { clearForm } from '../../features/guest/rsvpSlice';
import { storeCompletedRSVP, clearCompleteRSVPs } from '../../features/guest/rsvpCompletedSlice.js'
import { useRegisterRSVPMutation } from '../../services/gizmo.js'

// TODO: on desktop all the information is pushed down too far

export function RSVPFormSubmit({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {

    const dispatch = useDispatch();
    const [registerRSVP, { isLoading, isSuccess, isError, error }] = useRegisterRSVPMutation();

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode)
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)
    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const submitted = useSelector((state) => state.rsvp.submitted)
    const rsvpSubmission = useSelector((state) => state.rsvp.rsvpSubmission)
    const fullGuestInfo = useSelector((state) => state.rsvp)
    const completedRsvps = useSelector((state) => state.rsvpCompleted.completedRsvps);

    const handleSubmit = async (makeApiCall) => {
        // Step 1: Update Redux state
        const submissionKey = `${firstName}_${lastName}`;
        dispatch(storeCompletedRSVP({submissionKey, fullGuestInfo}));
        dispatch(clearForm())

        // Step 2: Make the API call
        if (!makeApiCall) return;

        try {
            const result = await registerRSVP({
            headers: { 'X-First-Last': submissionKey },
            rsvpData: { 'rsvps': completedRsvps },
            }).unwrap();

            console.log('RSVP(s) registered successfully:', result);
        } catch (err) {
            console.error('Error registering RSVP(s):', err);
        }
    };

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
            {rsvpCode.toUpperCase() === 'UNF' 
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
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' to='/rsvp/dietary' end><marquee>Return</marquee></NavLink> 

            {rsvpCode.toUpperCase() === 'FZN'
             ? <NavLink className='btn-23' id="vers1" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>

            : rsvpCode.toUpperCase() === 'UNF'
             ? <NavLink className='btn-23' id="vers2" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>
            
            : (rsvpCode.toUpperCase() === 'NZU' & submitted === null)
             ? <NavLink className='btn-23' id="vers3" to='/rsvp' onClick={() => handleSubmit(false)}>
                <marquee>Continue</marquee></NavLink>
            
            : (rsvpCode.toUpperCase() === 'NZU' & submitted != null)
             ? <NavLink className='btn-23' id="vers4" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>

            : <p>error you should not have gotten this far!!</p>}

        </CardStackFooter>
    </>
    )
}
