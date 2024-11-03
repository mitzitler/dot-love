// i need the rsvp_code here
import { useState } from "react";
import '../App.css';

const pronouns_list = {
  ff: "she/her",
  mm: "he/him",
  nn: "they/them",
  fn: "she/they",
  mn: "he/they"
}

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

export function RSVPFormMiddle({ children, rsvpCode, 
  firstName, setFirstName, 
  lastName, setLastName,
  pronouns, setPronouns,
  phoneNumber, setPhoneNumber,
  email, setEmail,
  streetAddress, setStreetAddress,
  secondAddress, setSecondAddress,
  zipcode, setZipcode,
  city, setCity,
  country, setCountry,
  stateProvince, setStateProvince}) {



  function handleFirstName(inputFirstName) {setFirstName(inputFirstName)} // interim variable for firstName
  function handleLastName(inputLastName) {setLastName(inputLastName)} // interim variable for lastName
  function handlePronouns(inputPronouns) {setPronouns(inputPronouns)}
  function handlePhoneNumber(inputPhoneNumber) {setPhoneNumber(inputPhoneNumber)}
  function handleEmail(inputEmail) {setEmail(inputEmail)}
  function handleStreetAddres(inputStreetAddress) {setStreetAddress(inputStreetAddress)} // interim variable for streetAddress
  function handleSecondAddress(inputSecondAddress) {setSecondAddress(inputSecondAddress)} // interim variable for secondAddress
  function handleZipcode(inputZipcode) {setZipcode(inputZipcode)}
  function handleCity(inputCity) {setCity(inputCity)} // interim variable for city
  function handleCountry(inputCountry) {setCountry(inputCountry)} // interim variable for country
  function handleStateProvince(inputStateProvince) {setStateProvince(inputStateProvince)} // interim variable for stateProvince

  const plus_one_code = "ABCD";

  return (
    <div class="rsvp">
      <div id="main">

        <h1>
          Please enter some personal info to RSVP
        </h1>

        <div>

          <h2>
            What do we call you?
          </h2>

          <div class="name-info">
            <input label="first-name" type="text" 
              id="first-name" 
              placeholder="First" 
              value={firstName} 
              onInput={e=>handleFirstName(e.target.value)}></input>
            <input label="last-name" type="text" 
              id="first-name" 
              placeholder="Last" 
              value={lastName} 
              onInput={e=>handleLastName(e.target.value)}></input>

            <drp id="pronouns" class="dropdown">
                {!pronouns ? <a>Pronouns</a> :
                  <a>{pronouns}</a>}
                <ul class="dropdown-content"
                  value={pronouns}>
                    {Object.keys(pronouns_list).map((pronounKey) => (
                      <li key={pronounKey} value={pronounKey} onClick={()=>handlePronouns(pronouns_list[pronounKey])}><a>
                        {pronouns_list[pronounKey]}
                      </a></li>
                  ))}
                </ul>
              </drp>
            {/* <input label="pronouns" type="text" 
              id="pronouns" 
              placeholder="Pronouns"
              value={pronouns}
              onInput={e=>handlePronouns(e.target.value)}></input> */}
          </div>

          <h2>
            How do we reach you?
          </h2>

          <div class="contact-num">
            <input label="phone" type="number" 
                id="phone"
                placeholder="Phone number" 
                value={phoneNumber}
                onInput={e=>handlePhoneNumber(e.target.value)}></input>
              <input label="email" type="text" 
                id="email"
                placeholder="Email" value={email} 
                onInput={e=>handleEmail(e.target.value)}></input>
            </div>

          <div class="contact-info">
            <input label="street-address" type="text" 
                id="address"
                placeholder="Street address" 
                value={streetAddress} 
                onInput={e=>handleStreetAddres(e.target.value)}></input>
              <input label="apt-num" type="text" 
                id="address-2"
                placeholder="Apt #" value={secondAddress} 
                onInput={e=>handleSecondAddress(e.target.value)}></input>
              <input label="city" type="text" 
                id="city"
                placeholder="City" value={city} onInput={e=>handleCity(e.target.value)}></input>
            </div>

            <div class="state-country">  
              <input label="zipcode" type="text" 
                id="zipcode"
                placeholder="Zip" 
                value={zipcode} 
                onInput={e=>handleZipcode(e.target.value)}></input>
              <drp id="country" class="dropdown state-country-item">
                {!country ? <a>Country</a> :
                  <a>{country}</a>}
                <ul class="dropdown-content"
                  value={country}>
                    {Object.keys(countries).map((countryKey) => (
                      <li key={countryKey} value={countryKey} onClick={()=>handleCountry(countries[countryKey])}><a>
                        {countries[countryKey]}
                      </a></li>
                  ))}
                </ul>
              </drp>

              <drp id="state" class="dropdown state-country-item">
                
              {!stateProvince ? <a>State/Province</a> :
                  <a>{stateProvince}</a>}
                <ul 
                // name="stateProvince" id="stateProvince" 
                  class="dropdown-content menu bg-neutral rounded-box z-[1] overflow-y-scroll max-h-72" 
                  value={stateProvince}>
                  {
                  country === "United States"
                  ? Object.keys(usStates).map((usStateKey) => (
                      <li key={usStateKey} value={usStateKey} onClick={()=>handleStateProvince(usStates[usStateKey])}><a>
                        {usStates[usStateKey]}
                      </a></li>
                  ))
                  : ( 
                    country === "Mexico"
                    ? Object.keys(mxStates).map((mxStateKey) => (
                      <li key={mxStateKey} value={mxStateKey} onClick={()=>handleStateProvince(mxStates[mxStateKey])}><a>
                        {mxStates[mxStateKey]}
                      </a></li>
                    ))
                    : ( 
                      country === "Canada"
                      ? Object.keys(caStates).map((caStateKey) => (
                        <li key={caStateKey} value={caStateKey} onClick={()=>handleStateProvince(caStates[caStateKey])}><a>
                          {caStates[caStateKey]}
                        </a></li>
                      ))
                      : <></>
                  ))
                  }
                </ul>
              </drp>
            </div> 

          </div>

        </div>
    </div>
  );
}

// if at the submit state and country dont match, raise an error

// this (in App.css) will hide the number incrementer
// input::-webkit-outer-spin-button,
// input::-webkit-inner-spin-button {
//     /* display: none; <- Crashes Chrome on hover */
//     -webkit-appearance: none;
//     margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
// }

// input[type=number] {
//     -moz-appearance:textfield; /* Firefox */
// }