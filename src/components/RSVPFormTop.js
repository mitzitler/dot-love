// i need the rsvp_code here
import { useState } from "react";
import nameReducer from "../features/guest/nameSlice";
import { store } from "../store"
import { useDispatch } from "react-redux"
import '../App.css';
import { nameRsvp } from "../features/guest/nameSlice";

export function RSVPFormTop({ children, rsvpCode, RsvpOptions, rsvp, setRsvp }) {

  // function handleRsvp(rsvpChoice) {setRsvp(rsvpChoice)} // interim variable for rsvp
  function handleRsvp(rsvpChoice) {dispatch(nameRsvp(rsvpChoice))} // interim variable for rsvp

  const guestType = 1.5
  const dispatch = useDispatch()
  // 1.5 open plus one, 2.0 is closed plus one
  // 2.5 is the invited plus one

  console.log(rsvp)

  return (
    <div class="rsvp">
      <div id="main">
        <h1>rEpOnDeZ SiL vOuS pLaIt</h1>
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
              // value="ATTENDING"
              value={RsvpOptions.ATTENDING}
              // onClick={() => dispatch(nameRsvp(RsvpOptions.ATTENDING))}
                onClick={e=>handleRsvp(RsvpOptions.ATTENDING)}
                ></input>
              <label for="rsvp-yes">
                I will be in attendance
              </label>
            </div>
            <div id="radio-item">
              <input id="rsvp-no" name="rsvp" type="radio"
                // value="NOT_ATTENDING"
                value={RsvpOptions.NOT_ATTENDING} 
                // onClick={() => dispatch(nameRsvp())}
                onClick={e=>handleRsvp(RsvpOptions.NOT_ATTENDING)}
                ></input>
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
      </div>
    </div>
  );
}
