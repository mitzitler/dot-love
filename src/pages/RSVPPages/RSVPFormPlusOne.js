import React from 'react';
import { useEffect, useState } from 'react';
import { NavLink, useSearchParams } from 'react-router-dom';
import '../../App.css';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useDispatch, useSelector } from 'react-redux';
import { rsvpStatusInput } from '../../features/guest/rsvpSlice';
import { useGetUserByGuestLinkQuery } from '../../services/gizmo.js'

export function RSVPFormPlusOne({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {
    // react hooks called at top level
    const dispatch = useDispatch();
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)
    const submitted = useSelector((state) => state.rsvp.submitted)

    // handle guest code query param
    const [searchParams] = useSearchParams();
    const code = searchParams.get('code');

    // API data
    const { data, error, isLoading } = useGetUserByGuestLinkQuery(code);
    const [guestData, setGuestData] = useState(null);
    useEffect(() => {
      if (data) {
        setGuestData(data);
      }
    }, [data]);


    // handle return
    if (isLoading) {
        return <p>Loading guest details...</p>;
    }
    if (error) {
      return <p>Error validating code. Please try again.</p>;
    }


    return
              {guestData ? (
        <>
             <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <h1>Repondez S'il Vous Plait!</h1>
                <div>
                    <h2>May we expect your presence at our wedding on <br></br>
                        November 7th, 2025 in Brooklyn, NY?</h2>
                    <p>If need be, you can change this, but please let us know soon!</p>
                </div>
                <div id="rsvp-radio">
                    <div id="radio-item">
                        <input id="rsvp-yes" name="rsvp" type="radio" value={rsvpStatus}
                            onClick={()=>dispatch(rsvpStatusInput("attending"))}></input>
                        <label className='radio-label' htmlFor="rsvp-yes">
                            Yes, I will be in attendance!
                        </label>
                    </div>
                    <div id="radio-item">
                        <input id="rsvp-no" name="rsvp" type="radio" value={rsvpStatus}
                            onClick={()=>dispatch(rsvpStatusInput("notattending"))}></input>
                        <label className='radio-label' htmlFor="rsvp-no">
                            No, unfortunately I cannot attend
                        </label>
                    </div>
                </div>

            </CardStackPage>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <NavLink className='btn-23'
                    disabled={rsvpStatus === 'undecided' ? true : false}
                    to={rsvpStatus === 'undecided' ? '/rsvp' : '/rsvp/contact'}
                    end><marquee>Continue</marquee></NavLink>
                    {/* and there needs to be an error message too */}
            </CardStackFooter> )
        </>
             ) : (
        <>
          {/* should probably switch this with a loading spinner */}
          <p>Invalid or missing guest code</p>
        </>

              )}
}
