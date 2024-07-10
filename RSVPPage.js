// i need the rsvp_code here
import { useState } from "react";

export function RSVPPage({ children }) {
  return (
    <div>
      <div>
        <h1>
          We are delighted to have you in addendance at our little wedding
          coming up. S'il te plait, reponds?{" "}
        </h1>
      </div>
      <div>{children}</div>
    </div>
  );
}

export function RSVPForm({ children, rsvpCode }) {
  const [fullName, setFullName] = useState("");
  const [guestStatus, setGuestStatus] = useState("regular");
  const [isLocal, setIsLocal] = useState(true);
  const [isAccompanied, setIsAccompanied] = useState(false);
  const [rsvp, setRsvp] = useState(false);

  function handleRsvp() {
    setRsvp(true);
    console.log("pussy");
  }

  const plus_one_code = "ABCD";
  const target_date = null;

  return (
    <div>
      <div id="wrapper">
        <p>
          <label for="yes_no_radio">
            May we expect your presence at our wedding?
          </label>
        </p>
        <ul>
          <span>I will be in attendance </span>
          <input type="radio" name="yes_no" checked></input>
        </ul>

        <ul>
          <span>Unfortunately I cannot attend </span>
          <input type="radio" name="yes_no"></input>
        </ul>
        {/* if no, pop up that says would you still like to fill out information!*/}
      </div>
      <div>
        <p>Please enter some personal information for your response</p>
        <ul>
          <span>Your full name, please </span>
          {/*
          <input type="text" onChange={() => setFullName()}>
            {fullName}
          </input>
        */}
        </ul>
        <ul>
          <span>Your pronouns, please </span>
          <input type="text"></input>
        </ul>
        <ul>
          <span>Your address, please</span>
          <input type="text"></input>
        </ul>
        <ul>
          <span>Any dietary restrictions, please</span>
          <ul>
            <input type="checkbox"></input>
            <label>No meat</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No fish or shellfish</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No eggs</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No dairy</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No gluten</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No peanuts or legumes</label>
          </ul>
          <ul>
            <input type="checkbox"></input>
            <label>No tree nuts</label>
          </ul>
          <ul>
            <input type="text" placeholder="Other restrictions"></input>
          </ul>
        </ul>
        {/*
        <label for="yes_no_radio">Do you plan on bringing a plus one?</label>
*/}
        <p>
          {/*
          <input type="radio" name="yes_no">
            Yes, and they will respond to this form by {target_date} using this
            code {plus_one_code}
          </input>
*/}
        </p>
        <p>
          {/*
          <input type="radio" name="yes_no">
            Unfortunately, my plus one cannot attend
          </input>{" "}
*/}
        </p>
        <h3>
          Please submit your RSVP for us - you will have the chance to change
          this is need be!
        </h3>
      </div>
      <RSVPFormSubmit handleRsvp={handleRsvp} />
    </div>
  );
}

export function RSVPFormSubmit({ handleRsvp }) {
  return (
    <button className="btn-submit-rsvp" onClick={() => handleRsvp()}>
      Submit RSVP !
    </button>
  );
}
