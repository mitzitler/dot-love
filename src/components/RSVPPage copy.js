// i need the rsvp_code here
import { useState } from "react";

export function RSVPPage({ children }) {
  return (
    <div>{children}</div>
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
    <div class="container mx-10 my-5">
      <div class="card my-10 items-center bg-accent bg-opacity-60">
        <h1 class="card-title p-10 text-xl font-semibold">rEpOnDeZ SiL vOuS pLaIt</h1>
        <div class="card-body pt-2 pb-20">
          <fieldset>
            <legend class="text-lg font-semibold">May we expect your presence at our wedding?</legend>
            <p class="text-sm leading-6 text-gray-600">If need be, you can change this, but please let us know soon!</p>
            <div class="mt-6">
              <div class="flex items-center gap-x-8">
                <input id="rsvp-yes" name="rsvp" type="radio" class="radio h-5 w-5 border-secondary border-2 radio-primary"></input>
                <label for="rsvp-yes" class="block text-md font-md">I will be in attendance</label>
              </div>
              <div class="flex items-center gap-x-8">
                <input id="rsvp-no" name="rsvp" type="radio" class="radio h-5 w-5 border-secondary border-2 radio-primary"></input>
                <label for="rsvp-no" class="block text-md font-md">Unfortunately I cannot attend</label>
              </div>
            </div>
          </fieldset>
        </div>
        {/* if no, pop up that says would you still like to fill out information!*/}
      </div>

      <div class="card my-10 items-center bg-accent bg-opacity-60">
        <h1 class="card-title p-10 text-xl font-semibold">Please enter some personal information to RSVP</h1>
        <div class="card-body pt-2 pb-20">
        <p class="text-sm px-5 leading-6 text-gray-600">Even if you can't make it, let us know! Your name, pronouns and contact info will help us communicate logistics.</p>
        <fieldset>
        {/*  <span class="block text-md px-10">What should we call you?</span> */}
          <div class="mt-5 sm:mt-8">
            <div class="flex flex-col sm:flex-row gap-3">
            {/*  <label for="first-name" class="block text-md">First name</label> */}
              <input label="first-name" type="text" class="input input-primary text-sm" placeholder="Your first name, please"></input>
              {/*
              <input type="text" onChange={() => setFullName()}>
              {fullName}
              </input>
              */}
            {/*  <label for="last-name" class="block text-md">Last name</label> */}
              <input label="last-name" type="text" class="input input-primary text-sm" placeholder="Your last name, please"></input>
              {/*
              <input type="text" onChange={() => setFullName()}>
              {fullName}
              </input>
              */}
            {/*  <label for="pronouns" class="block text-md">Pronouns</label>  ideally this is actually text / text */}
              <input label="pronouns" type="text" class="input input-primary text-sm" placeholder="Your pronouns, please"></input>
            </div>
            <div class="sm:col-span-4">
              <label for="street-address" class="block text-md">Street address</label>
              <input label="street=address" type="text" class="input input-primary h-6"></input>
            </div> {/*i think this should be broken out as well*/}
          </div>
          <div class="card">
            <span>Any dietary restrictions, please</span>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No meat</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No fish or shellfish</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No eggs</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No dairy</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No gluten</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No peanuts or legumes</label>
            </ul>
            <ul>
              <input type="checkbox" class="toggle toggle-primary"></input>
              <label>No tree nuts</label>
            </ul>
            <ul>
              <input type="text" placeholder="Other restrictions"></input>
            </ul>
          </div>
        </fieldset>
        </div>
      </div>
      <div>
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
          this is need be! {/*i want to put the button into this card but it needs a width rule*/}
        </h3>
      </div>
      <RSVPFormSubmit handleRsvp={handleRsvp} />
    </div>
  );
}

export function RSVPFormSubmit({ handleRsvp }) {
  return (
    <button data-theme='light' className="btn" onClick={() => handleRsvp()}>
      Submit RSVP !
    </button>
  );
}
