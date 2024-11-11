import '../../App.css';
import { NavLink } from 'react-router-dom';
import React from 'react';

export function RSVPFormContact({firstName, lastName, pronouns, phoneNumber, email,
    streetAddress, secondAddress, zipcode, city, country, stateProvince, dispatch}) {
  
    return (
        <>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
                <div class="rsvp">
                    <div id="main">
            
                    <h1>
                        Please enter some personal info...
                    </h1>
            
                    <div>
            
                        <h2>
                        What do we call you?
                        </h2>
                        {/* remove value={} in order for text to show up */}
            
                        <div class="name-info">
                        <input label="first-name" type="text" 
                            id="first-name" 
                            placeholder="First" 
                            onChange={()=>dispatch({type: "firstNameInput", payload: firstName })}></input>
                        <input label="last-name" type="text" 
                            id="first-name" 
                            placeholder="Last" 
                            value={lastName} 
                            onChange={()=>dispatch({type: "lastNameInput", payload: lastName })}></input>
            
                        <drp id="pronouns" class="dropdown">
                            {!pronouns ? <a>Pronouns</a> :
                                <a>{pronouns}</a>}
                            <ul class="dropdown-content"
                                value={pronouns}>
                                {Object.keys(pronouns_list).map((pronounKey) => (
                                    <li key={pronounKey} value={pronounKey} 
                                    onChange={()=>dispatch({type: "pronounsInput", payload: pronouns_list[pronounKey] })}
                                    ><a>
                                    {pronouns_list[pronounKey]}
                                    </a></li>
                                ))}
                            </ul>
                            </drp>
                        </div>
            
                        <h2>
                        How do we reach you?
                        </h2>
            
                        <div class="contact-num">
                        <input label="phone" type="number" 
                            id="phone"
                            placeholder="Phone number" 
                            value={phoneNumber}
                            onChange={()=>dispatch({type: "phoneNumberInput", payload: phoneNumber})}></input>
                            <input label="email" type="text" 
                            id="email"
                            placeholder="Email" value={email} 
                            onChange={()=>dispatch({type: "emailInput", payload: email})}></input>
                        </div>
            
                        <div class="contact-info">
                        <input label="street-address" type="text" 
                            id="address"
                            placeholder="Street address" 
                            value={streetAddress} 
                            onChange={()=>dispatch({type: "streetAddressInput", payload: streetAddress})}></input>
                            <input label="apt-num" type="text" 
                            id="address-2"
                            placeholder="Apt #" value={secondAddress} 
                            onChange={()=>dispatch({type: "secondAddressInput", payload: secondAddress})}></input>
                            <input label="city" type="text" 
                            id="city" placeholder="City" value={city}
                            onChange={()=>dispatch({type: "cityInput", payload: city})}></input>
                        </div>
            
                        <div class="state-country">  
                            <input label="zipcode" type="text" 
                            id="zipcode"
                            placeholder="Zip" 
                            value={zipcode} 
                            onChange={()=>dispatch({type: "zipcodeInput", payload: zipcode})}></input>
                            <drp id="country" class="dropdown state-country-item">
                            {!country ? <a>Country</a> :
                                <a>{country}</a>}
                            <ul class="dropdown-content"
                                value={country}>
                                {Object.keys(countries).map((countryKey) => (
                                    <li key={countryKey} value={countryKey}
                                    // onClick={()=>handleCountry(countries[countryKey])}
                                    onChange={()=>dispatch({type: "countryInput", payload: countries[countryKey]})}
                                    ><a>
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
                                    <li key={usStateKey} value={usStateKey} 
                                    // onClick={()=>handleStateProvince(usStates[usStateKey])}
                                    onChange={()=>dispatch({type: "stateProvinceInput", payload: usStates[usStateKey]})}><a>
                                    {usStates[usStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                country === "Mexico"
                                ? Object.keys(mxStates).map((mxStateKey) => (
                                    <li key={mxStateKey} value={mxStateKey} 
                                    // onClick={()=>handleStateProvince(mxStates[mxStateKey])}
                                    onChange={()=>dispatch({type: "stateProvinceInput", payload: mxStates[mxStateKey]})}><a>
                                    {mxStates[mxStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                    country === "Canada"
                                    ? Object.keys(caStates).map((caStateKey) => (
                                    <li key={caStateKey} value={caStateKey} 
                                    // onClick={()=>handleStateProvince(caStates[caStateKey])}
                                    onChange={()=>dispatch({type: "stateProvinceInput", payload: caStates[caStateKey]})}><a>
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
                        <span>
                            <NavLink className='next-btn' to='/' end>Go back?</NavLink> 
                            <NavLink className='next-btn' to='/contact' end>Continue...</NavLink> 
                        </span>
            
                    </div>
                </div>
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        </>
    );
  }


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