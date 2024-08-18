// i need the rsvp_code here
import { useState } from "react";
import { GradientComponent } from "./Gradient";
import '../App.css';

export function RSVPPage({ children }) {
  return (
   /* <div>{children}</div> */
   <div id = "gradient">
      <GradientComponent/>
      <div id="overlay">{children}</div>
    </div>
  );
}

const RsvpOptions = Object.freeze({
  ATTENDING: "ATTENDING",
  NOT_ATTENDING: "NOT_ATTENDING",
  UNDECIDED: "UNDECIDED"
});

const countries = {
  us: "United States",
  mx: "Mexico",
  ca: "Canada"
}

const usStates = {
  al: "Alabama", ak: "Alaska", az: "Arizona", ar: "Arkansas", ca: "California", co: "Colorado",
  cn: "Connecticut", dc: "D.C.", de: "Delaware", fl: "Florida", ga: "Georgia", hi: "Hawaii", 
  id: "Idaho", il: "Illinois", in: "Indiana", ia: "Iowa", ks: "Kansas", ky: "Kentucky", la: "Louisiana",
  me: "Maine", md: "Maryland", ma: "Massachusetts", mi: "Michigan", mn: "Minnesota", ms: "Mississippi",
  mo: "Missouri", mt: "Montana", ne: "Nebraska", nv: "Nevada", nh: "New Hampshire", nj: "New Jersey",
  nm: "New Mexico", ny: "New York", nc: "North Carolina", nd: "North Dakota", oh: "Ohio", ok: "Oklahoma",
  or: "Oregon", pa: "Pennsylvania", pr: "Puerto Rico", ri: "Rhode Island", sc: "South Carolina",
  sd: "South Dakota", tn: "Tennessee", tx: "Texas", ut: "Utah", vt: "Vermont", va: "Virginia",
  wa: "Washington", wv: "West Virginia", wi: "Wisconsin", wy: "Wyoming"
}

const mxStates = {
  ag: "Aguascalientes", bn: "Baja California", bs: "Baja California Sur", cp: "Campeche", cs: "Chiapas",
  ci: "Chihuaha", ch: "Coahuila", cl: "Colima", dg: "Durango", gj: "Guanajuato", ge: "Guerrero", 
  hd: "Hidalgo", ja: "Jalisco", mx: "Mexico", df: "Mexico City", mc: "Michoacan", mr: "Morelos",
  na: "Nayarit", nl: "Nuevo Leon", oa: "Oaxaca", pu: "Puebla", qe: "Queretaro", qi: "Quintana Roo",
  sl: "San Luis Potosi", si: "Sinaloa", so: "Sonora", tb: "Tobasco", ta: "Tamaulipas", tl: "Tlaxcala",
  vc: "Veracruz", yu: "Yucatan", za: "Zacatecas"
}

const caStates = {
  ab: "Alberta", bc: "British Columbia", mb: "Monitoba", nb: "New Brunswick", 
  nl: "Newfoundland and Labrador", nt: "Northwest Territories", ns: "Nova Scotia", nu: "Nunavut",
  on: "Ontario", pe: "Prince Edward Island", qc: "Quebec", sk: "Saskatchewan", yt: "Yukon"
}

export function RSVPForm({ children, rsvpCode }) {
  const [rsvp, setRsvp] = useState(RsvpOptions.UNDECIDED);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [pronouns, setPronouns] = useState("")
  const [streetAddress, setStreetAddress] = useState('')
  const [secondAddress, setSecondAddress] = useState('')
  const [city, setCity] = useState('')
  // should have a zipcode field too
  const [country, setCountry] = useState('')
  const [stateProvince, setStateProvince] = useState('New York')


  //const [guestStatus, setGuestStatus] = useState("regular");
  //const [isLocal, setIsLocal] = useState(true);
  //const [isAccompanied, setIsAccompanied] = useState(false);

  console.log(firstName)

  function handleRsvp(rsvpChoice) {setRsvp(rsvpChoice)} // interim variable for rsvp
  function handleFirstName(inputFirstName) {setFirstName(inputFirstName)} // interim variable for firstName
  function handleLastName(inputLastName) {setLastName(inputLastName)} // interim variable for lastName
  // function handlePronouns
  function handleStreetAddres(inputStreetAddress) {setStreetAddress(inputStreetAddress)} // interim variable for streetAddress
  function handleSecondAddress(inputSecondAddress) {setSecondAddress(inputSecondAddress)} // interim variable for secondAddress
  function handleCity(inputCity) {setCity(inputCity)} // interim variable for city
  // function handleZip
  function handleCountry(inputCountry) {
    setCountry(inputCountry)
    console.log(inputCountry)
  } // interim variable for country
  function handleStateProvince(inputStateProvince) {setStateProvince(inputStateProvince)} // interim variable for stateProvince

  const plus_one_code = "ABCD";
  const target_date = null;

  console.log(rsvp)
  console.log(firstName)
  console.log(lastName)
  console.log(streetAddress)
  console.log(secondAddress)
  console.log(city)
  console.log(country)

  return (
    <div class="container m-10 m-auto">
      <div class="card my-10 items-center bg-accent bg-opacity-60">
        <h1 class="card-title p-10 text-xl font-semibold">rEpOnDeZ SiL vOuS pLaIt</h1>
        <div class="card-body pt-2 pb-20">
          <fieldset>
            <legend class="text-lg font-semibold">May we expect your presence at our wedding on November 7th, 2025 in Brooklyn, NY?</legend>
            <p class="text-sm leading-6 text-gray-600">If need be, you can change this, but please let us know soon!</p>
            <div class="mt-6">
              <div class="flex items-center gap-x-8">
                <input id="rsvp-yes" name="rsvp" type="radio" class="radio h-5 w-5 border-secondary border-2 radio-primary"
                value={rsvp} onClick={e=>handleRsvp(RsvpOptions.ATTENDING)}></input>
                <label for="rsvp-yes" class="block text-md font-md">I will be in attendance</label>
              </div>
              <div class="flex items-center gap-x-8">
                <input id="rsvp-no" name="rsvp" type="radio" class="radio h-5 w-5 border-secondary border-2 radio-primary"
                  value={RsvpOptions.NOT_ATTENDING} onClick={e=>handleRsvp(RsvpOptions.NOT_ATTENDING)}></input>
                <label for="rsvp-no" class="block text-md font-md">Unfortunately I cannot attend</label>
              </div>
            </div>
          </fieldset>
        </div>
      </div>

      <div class="card my-10 items-center bg-accent bg-opacity-60">
        <h1 class="card-title p-10 text-xl font-semibold">Please enter some personal information to RSVP</h1>
        <div class="card-body pt-2 pb-20">
        {/*<p class="text-sm px-5 leading-6 text-gray-600">Even if you can't make it, let us know! Your name, pronouns and contact info will help us communicate logistics.</p> */}
        <fieldset>
        {/*  <span class="block text-md px-10">What should we call you?</span> */}
          <div class="mt-5 sm:mt-8">
            <div class="m-auto grid grid-cols-8 gap-2">
              <input label="first-name" type="text" class="input input-primary col-span-3 py-4 text-sm" 
              placeholder="Your first name, please" value={firstName} onInput={e=>handleFirstName(e.target.value)}></input>
              <input label="last-name" type="text" class="input input-primary col-span-3 py-4 text-sm" 
              placeholder="Your last name, please" value={lastName} onInput={e=>handleLastName(e.target.value)}></input>
            {/*  <label for="pronouns" class="block text-md">Pronouns</label>  ideally this is actually text / text */}
              <input label="pronouns" type="text" class="input input-primary col-span-2 py-4 text-sm" 
              placeholder="Pronouns"></input>
              <input label="street-address" type="text" class="input input-primary col-span-2 my-4 py-4 text-sm" 
              placeholder="Street address" value={streetAddress} onInput={e=>handleStreetAddres(e.target.value)}></input>
              <input label="apt-num" type="text" class="input input-primary col-span-1 my-4 py-4 text-sm" 
              placeholder="Apt #" value={secondAddress} onInput={e=>handleSecondAddress(e.target.value)}></input>
              <input label="city" type="text" class="input input-primary col-span-2 my-4 py-4 text-sm" 
              placeholder="City" value={city} onInput={e=>handleCity(e.target.value)}></input>
              <div class="dropdown dropdown-hover col-span-1 my-0 py-4 text-sm">
                <btn role="button" class="btn border-primary my-0 w-max h-max">Country</btn>
                <ul name="country" id="country" 
                class="dropdown-content menu bg-neutral rounded-box shadow z-[1] overflow-x-auto"
                value={country}>
                  {Object.keys(countries).map((countryKey) => (
                      <li key={countryKey} value={countryKey} onClick={()=>handleCountry(countries[countryKey])}><a>
                        {countries[countryKey]}
                      </a></li>
                  ))}
                </ul>
              </div>
              <div class="dropdown dropdown-hover flex my-0 py-4 text-sm">
                <div  role="button" class="btn border-primary my-0">State / Province</div>
                <ul name="stateProvince" id="stateProvince" 
                class="dropdown-content menu bg-neutral rounded-box z-[1] overflow-y-scroll max-h-72" 
                value={stateProvince}>
                  {
                  country === "United States"
                  ? Object.keys(usStates).map((usStateKey) => (
                      <li key={usStateKey} value={usStateKey} onClick={()=>handleCountry(usStates[usStateKey])}><a>
                        {usStates[usStateKey]}
                      </a></li>
                  ))
                  : ( 
                    country === "Mexico"
                    ? Object.keys(mxStates).map((mxStateKey) => (
                      <li key={mxStateKey} value={mxStateKey} onClick={()=>handleCountry(mxStates[mxStateKey])}><a>
                        {mxStates[mxStateKey]}
                      </a></li>
                    ))
                    : ( 
                      country === "Canada"
                      ? Object.keys(caStates).map((caStateKey) => (
                        <li key={caStateKey} value={caStateKey} onClick={()=>handleCountry(caStates[caStateKey])}><a>
                          {caStates[caStateKey]}
                        </a></li>
                      ))
                      : <></>
                  ))
                  }
                </ul>
              </div>
            </div> 
          </div>
          <div class="card">
            <span>Any dietary restrictions, please</span>
            {/*it would be cool if this section was actually a checkbox where you click stuff and it x's out like ghostbusters */}
            <img src="../images/dietary-restrictions/alcohol_1.png" alt="I drink alcohol" width="500" height="600"></img>
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
        {/* if rsvp no, pop up that says would you still like to fill out information!*/}
      Submit RSVP !
    </button>
  );
}

{/* -- this is the list of state abbreviations

                  <li><a>AK</a></li> <li><a>AL</a></li> <li><a>AR</a></li> <li><a>AS</a></li> <li><a>AZ</a></li>
                  <li><a>CA</a></li> <li><a>CO</a></li> <li><a>CT</a></li> <li><a>DC</a></li> <li><a>DE</a></li>
                  <li><a>FL</a></li> <li><a>GA</a></li> <li><a>GU</a></li> <li><a>HI</a></li> <li><a>IA</a></li>
                  <li><a>ID</a></li> <li><a>IL</a></li> <li><a>IN</a></li> <li><a>KS</a></li> <li><a>KY</a></li>
                  <li><a>LA</a></li> <li><a>MA</a></li> <li><a>MD</a></li> <li><a>ME</a></li> <li><a>MI</a></li>
                  <li><a>MN</a></li> <li><a>MO</a></li> <li><a>MS</a></li> <li><a>MT</a></li> <li><a>NC</a></li>
                  <li><a>ND</a></li> <li><a>NE</a></li> <li><a>NH</a></li> <li><a>NJ</a></li> <li><a>NM</a></li>
                  <li><a>NY</a></li> <li><a>OH</a></li> <li><a>OK</a></li> <li><a>OR</a></li> <li><a>PA</a></li>
                  <li><a>PR</a></li> <li><a>RI</a></li> <li><a>SC</a></li> <li><a>SD</a></li> <li><a>TN</a></li>
                  <li><a>TX</a></li> <li><a>UT</a></li> <li><a>VA</a></li> <li><a>VI</a></li> <li><a>VT</a></li>
                  <li><a>WA</a></li> <li><a>WI</a></li> <li><a>WV</a></li> <li><a>WY</a></li> 

*/}