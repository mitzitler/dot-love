import React from 'react';
import { useEffect, useState } from 'react';
import { NavLink, useSearchParams } from 'react-router-dom';
import '../../App.css';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useDispatch, useSelector } from 'react-redux';
import { rsvpStatusInput, rsvpCodeInput } from '../../features/guest/rsvpSlice';
import { clearCompleteRSVPs } from '../../features/guest/rsvpCompletedSlice';
import { useGetUserByGuestLinkQuery } from '../../services/gizmo.js'
import { toast } from 'react-toastify'; // Toast (yum!)

export function RSVPFormPlusOne({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection}) {
    // react hooks called at top level
    const dispatch = useDispatch();
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)

    // handle guest code query param
    const [searchParams] = useSearchParams();
    const code = searchParams.get('code');

    // clear any lingering form
    dispatch(clearCompleteRSVPs())

    // Function to emit toast 🍞
    const notify = (input) => {
        toast.info(input, {
            theme: "dark",
            position: "top-right",
            icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30 }} alt='💕' />
        })
    }

    // API data
    const { data, isLoading, error } = useGetUserByGuestLinkQuery(code);
    const [, setGuestData] = useState(null);
    useEffect(() => {
      if (data) {
        setGuestData(data);
      }
      if (error) {
        console.error("Failed to fetch guest link data:", error);
        let errorMessage = "Failed to load guest information. Please check your link.";
        if (error.status === 404) {
            errorMessage = "Invalid or expired guest link. Please contact the hosts.";
        } else if (error.status === 500) {
            errorMessage = "Server error. Please try again later or contact the hosts.";
        } else if (error.originalStatus === undefined) {
            errorMessage = "Network error. Please check your connection and try again.";
        }
        toast.error(errorMessage, {
            theme: "dark",
            position: "top-right",
            autoClose: 7000,
        });
      }
    }, [data, error]);


    // handle return
    if (isLoading) {
        console.log(isLoading)
        return (<p>Loading guest details...</p>);
    }
    if (error) {
        return (
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <h1>Oops! Unable to load guest information</h1>
                <p>Please check your guest link or contact the hosts.</p>
            </CardStackPage>
        );
    }
    if (data) {
        console.log(isLoading)

        return (<><CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
        <h1>Hello, guest of {data.user.first} {data.user.last}!</h1>


        { notify("Guest link accepted! Please Scroll down")}
        {/* HACK: Technically there is no rsvpCode for a plus one, but we use fzn to note they do not get a plus 1 */}
        {/* { dispatch(rsvpCodeInput('fzn')) } */}
        <div>
            <h2>May we expect your presence at our wedding on <br></br>
                November 7th, 2025 in Brooklyn, NY?</h2>
            <p>If need be, you can change this, but please let us know soon!</p>
        </div>
        <div id="rsvp-radio">
            <div id="radio-item">
                <input id="rsvp-yes" name="rsvp" type="radio" value={rsvpStatus}
                    onClick={()=>{
                        dispatch(rsvpStatusInput("attending"));
                        dispatch(rsvpCodeInput('fzn'))
                        }}></input>
                <label className='radio-label' htmlFor="rsvp-yes">
                    Yes, I will be in attendance!
                </label>
            </div>
            <div id="radio-item">
                <input id="rsvp-no" name="rsvp" type="radio" value={rsvpStatus}
                    onClick={()=>{
                        dispatch(rsvpStatusInput("notattending"));
                        dispatch(rsvpCodeInput('fzn'))
                        }}></input>
                <label className='radio-label' htmlFor="rsvp-no">
                    No, unfortunately I cannot attend
                </label>
            </div>
        </div>

    </CardStackPage>

            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <NavLink className='btn-23'
                    disabled={rsvpStatus === 'undecided' ? true : false}
                    to={rsvpStatus !== 'undecided' ? '/rsvp/contact' : '/'}
                    end><marquee>Continue</marquee></NavLink>
                    {/* and there needs to be an error message too */}
            </CardStackFooter>
            </>
        );
    }

    return null;
}
