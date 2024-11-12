import '../../App.css';
import { NavLink } from 'react-router-dom';
import React from 'react';

export function RSVPFormContact({pronouns, country, stateProvince, dispatch}) {
  
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
                            onChange={(e)=>dispatch({type: "firstNameInput", payload: e.target.value })}></input>
                        <input label="last-name" type="text" 
                            id="first-name" 
                            placeholder="Last" 
                            onChange={(e)=>dispatch({type: "lastNameInput", payload: e.target.value })}></input>
            
                        <drp id="pronouns" class="dropdown">
                            {!pronouns ? <a>Pronouns</a> :
                                <a>{pronouns}</a>}
                            <ul class="dropdown-content">
                                {Object.keys(pronouns_list).map((pronounKey) => (
                                    <li key={pronounKey} 
                                    onClick={(e)=>dispatch({type: "pronounsInput", payload: pronouns_list[pronounKey]})}
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
                            onChange={(e)=>dispatch({type: "phoneNumberInput", payload: e.target.value})}></input>
                            <input label="email" type="text" 
                            id="email"
                            placeholder="Email"
                            onChange={(e)=>dispatch({type: "emailInput", payload: e.target.value})}></input>
                        </div>
            
                        <div class="contact-info">
                        <input label="street-address" type="text" 
                            id="address"
                            placeholder="Street address" 
                            onChange={(e)=>dispatch({type: "streetAddressInput", payload: e.target.value})}></input>
                        <input label="apt-num" type="text" 
                            id="address-2"
                            placeholder="Apt #" 
                            onChange={(e)=>dispatch({type: "secondAddressInput", payload: e.target.value})}></input>
                        <input label="city" type="text" 
                            id="city" placeholder="City" 
                            onChange={(e)=>dispatch({type: "cityInput", payload: e.target.value})}></input>
                        </div>
            
                        <div class="state-country">  
                            <input label="zipcode" type="text" 
                            id="zipcode"
                            placeholder="Zip" 
                            onChange={(e)=>dispatch({type: "zipcodeInput", payload: e.target.value})}></input>
                            <drp id="country" class="dropdown state-country-item">
                            {!country ? <a>Country</a> :
                                <a>{country}</a>}
                            <ul class="dropdown-content">
                                {Object.keys(countries).map((countryKey) => (
                                    <li key={countryKey} 
                                    onClick={()=>dispatch({type: "countryInput", payload: countries[countryKey]})}
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
                                class="dropdown-content menu bg-neutral rounded-box z-[1] overflow-y-scroll max-h-72">
                                {
                                country === "United States"
                                ? Object.keys(usStates).map((usStateKey) => (
                                    <li key={usStateKey}
                                    onClick={()=>dispatch({type: "stateProvinceInput", payload: usStates[usStateKey]})}><a>
                                    {usStates[usStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                country === "Mexico"
                                ? Object.keys(mxStates).map((mxStateKey) => (
                                    <li key={mxStateKey}
                                    onClick={()=>dispatch({type: "stateProvinceInput", payload: mxStates[mxStateKey]})}><a>
                                    {mxStates[mxStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                    country === "Canada"
                                    ? Object.keys(caStates).map((caStateKey) => (
                                    <li key={caStateKey} 
                                    onClick={()=>dispatch({type: "stateProvinceInput", payload: caStates[caStateKey]})}><a>
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
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
                <span className='button-container'>
                    <NavLink className='next-btn' to='/' end>Go back?</NavLink> 
                    <NavLink className='next-btn' to='/dietary' end>Continue...</NavLink> 
                </span>
            </section>
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