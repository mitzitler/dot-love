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
import { useRegisterUserMutation } from '../../services/gizmo';

// on desktop all the information is pushed down too far

export function RSVPFormSubmit({pageMainColor, pageSection}) {

    const dispatch = useDispatch();

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode)
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)
    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const submitted = useSelector((state) => state.rsvp.submitted)
    const rsvpSubmission = useSelector((state) => state.rsvp.rsvpSubmission)
    const fullGuestInfo = useSelector((state) => state.rsvp)

    const [registerUser] = useRegisterUserMutation();

    console.log(fullGuestInfo)

    const name = firstName + " " + lastName

    const rsvpString = rsvpStatus === "attending" ? "We are excited you are coming!" :
        "Sorry to hear you can't make it, but thank you for RSVPing anyway, and providing these details."

    const [dateLinkRequested, setDateLinkRequested] = useState(false)

    function handleDateLinkRequested() {
        setDateLinkRequested(!dateLinkRequested);
        console.log('text me a link: ' + !dateLinkRequested)
    }

    async function handleSubmit() {
        const registrationFields = {
            rsvp_status: rsvpStatus.toUpperCase(),
            pronouns,
            street: '221 s 3rd st',
            second_line: '5b',
            city: 'brooklyn',
            country: 'united states',
            state_loc: 'new york',
            phone: '+15046387943', // Replace with actual phone
            email: 'mitzitler@gmail.com', // Replace with actual email
            alcohol: true,
            meat: true,
            dairy: true,
            fish: true,
            shellfish: true,
            eggs: true,
            gluten: true,
            peanuts: true,
            restrictions: 'none',
            pair_first_last: '',
            rsvp_code: rsvpCode,
            zipcode: '11211',
        };

        const payload = {
            registration_fields: registrationFields,
            guest_link: dateLinkRequested ? 'requested' : '',
        };

        try {
            const response = await registerUser({
                headers: { 'X-First-Last': `${firstName}_${lastName}` },
                body: payload,
            }).unwrap();

            console.log('Registration Successful:', response);

            // Dispatch Redux action to store completed RSVP
            dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
        } catch (error) {
            console.error('Registration Failed:', error);
        }
    }

  return(
    <>
        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
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
                        Check this box to be texted a unique link for your guest to RSVP. This link will be active until August 7th, 2024 - three months before the wedding.
                        <input
                          id="guest-yes"
                          name="guest-yes"
                          type="checkbox"
                          checked={dateLinkRequested}
                          onChange={()=>handleDateLinkRequested()}
                        />
                        <span class="checkmark"></span>
                    </label>
                </div>
            </div>
            :<></>}

        </CardStackPage>
        <CardStackFooter>
            <NavLink className='btn-23' to='/rsvp/dietary' end>
              <marquee>
                Return
              </marquee>
            </NavLink>
            <NavLink className="btn-23" to="/" onClick={handleSubmit}>
                <marquee>
                  Submit
                </marquee>
            </NavLink>

            {rsvpCode.toUpperCase() === 'ABC'
            ? <NavLink className='btn-23' to='/' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Submit</marquee></NavLink>

            : rsvpCode.toUpperCase() === 'DEF'
            ? <NavLink className='btn-23' to='/' onClick={()=>{
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
            ? <NavLink className='btn-23' to='/' onClick={()=>{
                dispatch(storeCompletedRSVP([`${firstName}_${lastName}`, fullGuestInfo]));
                dispatch()
                }
            }><marquee>Submit</marquee></NavLink>
            
            : <p>error you should not have gotten this far!!</p>}

        </CardStackFooter>
    </>
    )
}
