import '../../App.css';
import { NavLink, useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { FormSubmitLeft } from '../../components/FormSubmitLeft.js';
import { FormSubmitRight } from '../../components/FormSubmitRight.js';
import { useDispatch, useSelector } from 'react-redux';
import { clearForm, phoneNumberInput, dateLinkRequestedInput } from '../../features/guest/rsvpSlice';
import { storeCompletedRSVP, clearCompleteRSVPs, setSubmitted } from '../../features/guest/rsvpCompletedSlice.js'
import { useRegisterRSVPMutation } from '../../services/gizmo.js'
import { store } from '../../store'

// TODO: on desktop all the information is pushed down too far

export function RSVPFormSubmit({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {
    const dispatch = useDispatch();
    const [registerRSVP, { isLoading, isSuccess, isError, error }] = useRegisterRSVPMutation();

    const guestCode = useSelector((state) => state.rsvp.guestCode) 
    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode);
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus);
    const firstName = useSelector((state) => state.rsvp.firstName);
    const lastName = useSelector((state) => state.rsvp.lastName);
    const pronouns = useSelector((state) => state.rsvp.pronouns);
    const email = useSelector((state) => state.rsvp.email);
    const phoneNumber = useSelector((state) => state.rsvp.phoneNumber);
    const fullGuestInfo = useSelector((state) => state.rsvp);
    const completedRsvps = useSelector((state) => state.rsvpCompleted.completedRsvps);
    const submitted = useSelector((state) => state.rsvpCompleted.submitted);

    const handleSubmit = async (makeApiCall) => {
        // Update the completed set of RSVPs with the latest rsvp
        dispatch(storeCompletedRSVP(fullGuestInfo));

        // We submitted an rsvp, so mark this so we remember if there are two for this call
        dispatch(setSubmitted(true));

        // Clear the form that gets filled out
        dispatch(clearForm());

        // If this is the second RSVP submitted, we will make the API call,
        // if this is the first, we may or may not
        if (!makeApiCall || isLoading) return;

        // NOTE: Since redux is async, we don't know if completedRsvps
        //       is updated or not. To account for this, combine it with
        //       the lastest rsvp and then just remove duplicates if present.
        const uniqueRsvpsToSubmit = Array.from(
            new Map(
                [...completedRsvps, fullGuestInfo].map(rsvp => [rsvp.firstName, rsvp])
            ).values()
        );

        // Make the API call
        try {
            const firstLast = `${firstName}_${lastName}`;
            const result = await registerRSVP({
                headers: { 'X-First-Last': firstLast },
                // NOTE: so we don't run into a
                rsvpData: uniqueRsvpsToSubmit,
            }).unwrap();

            if (result.code !== 200) {
                console.error("Something went wrong with Gizmo!", result);
                return cleanup();
            }

            console.log("Submitted RSVP(s) to the Gizmo, result:", result);
            cleanup();
        } catch (err) {
            console.error("RSVP(s) API call failed:", err);
            cleanup();
        }
    }

    const cleanup = () => {
        dispatch(clearForm());
        dispatch(clearCompleteRSVPs());
    };


    const name = firstName + " " + lastName
    const rsvpString = rsvpStatus === "attending" ? "We are excited you are coming!" :
        "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    function handleDateLinkRequested() {
        dispatch(dateLinkRequestedInput())
    }

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
            <h1 id="submit-header1">How's this, {name}?</h1>
            <p id="submit-header2">({pronouns})</p>
            <p id="submit-header3">{phoneNumber} - {email}</p>
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
                            onClick={(e)=>dispatch(dateLinkRequestedInput())}/>
                        <span class="checkmark"></span>
                    </label>
                </div>
            </div>
            :<></>}

        </CardStackPage>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' to='/rsvp/dietary' end><marquee>Return</marquee></NavLink> 

            {rsvpCode.toUpperCase() === 'FZN' || guestCode
             ? <NavLink className='btn-23' id="vers1" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>

            : rsvpCode.toUpperCase() === 'UNF'
             ? <NavLink className='btn-23' id="vers2" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>
            
             : (rsvpCode.toUpperCase() === 'NZU' && !submitted)
             ? <NavLink className='btn-23' id="vers3" to='/rsvp' onClick={() => handleSubmit(false)}>
                <marquee>Continue</marquee></NavLink>
            
            : (rsvpCode.toUpperCase() === 'NZU' && submitted)
             ? <NavLink className='btn-23' id="vers4" to='/rsvp/confirmation' onClick={() => handleSubmit(true)}>
                <marquee>Submit</marquee></NavLink>

            : <p>error you should not have gotten this far!!</p>}

        </CardStackFooter>
    </>
    )
}
