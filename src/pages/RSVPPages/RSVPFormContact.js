import '../../App.css';
import { NavLink } from 'react-router-dom';
import React from 'react';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useDispatch, useSelector } from 'react-redux';
import { firstNameInput, lastNameInput, pronounsInput, 
    phoneNumberCountryCodeInput, phoneNumberInput, emailInput,
    streetAddressInput, secondAddressInput, cityInput, zipcodeInput,
    countryInput, stateProvinceInput, continueDietary } from '../../features/guest/rsvpSlice';
import { toast } from 'react-toastify'; // Toast (yum!)

export function RSVPFormContact({pageMainColor, pageSecondaryColor, pageTertiaryColor, opacity, pageSection}) {

    const dispatch = useDispatch();

    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const phoneNumberCountryCode = useSelector((state) => state.rsvp.phoneNumberCountryCode)
    const phoneNumber = useSelector((state) => state.rsvp.phoneNumber)
    const email = useSelector((state) => state.rsvp.email)
    const streetAddress = useSelector((state) => state.rsvp.streetAddress)
    const secondAddress = useSelector((state) => state.rsvp.secondAddress)
    const city = useSelector((state) => state.rsvp.city)
    const zipcode = useSelector((state) => state.rsvp.zipcode)
    const country = useSelector((state) => state.rsvp.country)
    const stateProvince = useSelector((state) => state.rsvp.stateProvince)
    const canContinueDietary = useSelector((state) => state.rsvp.canContinueDietary)    
    
    // Function to emit toast 🍞
    const notify = (input) => {
        toast.info(input, {
            theme: "dark",
            position: "top-right",
            icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30, zIndex: 1000}} alt='💕' />
        })
    }

    return (
        <>
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} opacity={opacity} pageSection={pageSection}>
                <h1>Please enter some personal info...</h1>    

                {/* <div className={`section-content swipe-card flex-grow bg-lilac-400/65 border-lilac-500/50 border-1 backdrop-blur-md`}/> */}
                
                <div>
                    <h2>What do we call you?</h2>            
                    <div class="name-info">
                        <input label="first-name" type="text" 
                            id="first-name" 
                            placeholder="First"
                            value={firstName}
                            onChange={(e)=>
                                {dispatch(firstNameInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <input label="last-name" type="text" 
                            id="first-name" 
                            placeholder="Last" 
                            value={lastName}
                            onChange={(e)=>
                                {dispatch(lastNameInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <button id="pronouns" class="dropdown">
                            {!pronouns ? <a>Pronouns</a> :
                            <a>{pronouns}</a>}
                            <ul class="dropdown-content">
                                {Object.keys(pronouns_list).map((pronounKey) => (
                                    <li key={pronounKey} 
                                        onClick={(e)=>
                                        {dispatch(pronounsInput(pronouns_list[pronounKey]));
                                        dispatch(continueDietary())
                                        }
                                        }><a>
                                    {pronouns_list[pronounKey]}
                                    </a></li>
                                ))}
                            </ul>
                        </button>
                    </div>
                    <h2>How do we reach you?</h2>
                    <h3>Make sure to give us your phone number AND country code </h3>
                    <div class="contact-num">
                        <span>+</span>
                        <input label="country_code"
                            id="country-code"
                            value={phoneNumberCountryCode}
                            placeholder='1'
                            onChange={(e)=>
                                {dispatch(phoneNumberCountryCodeInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <input label="phone" 
                            id="phone"
                            placeholder="Phone number" 
                            value={phoneNumber}
                            onChange={(e)=>
                                {dispatch(phoneNumberInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <input label="email" type="text" 
                            id="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e)=>
                                {dispatch(emailInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                    </div>
    
                    <div class="contact-info">
                        <input label="street-address" type="text" 
                            id="address"
                            placeholder="Street address" 
                            value={streetAddress}
                            onChange={(e)=>
                                {dispatch(streetAddressInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <input label="apt-num" type="text" 
                            id="address-2"
                            placeholder="Apt #" 
                            value={secondAddress}
                            onChange={(e)=> {dispatch(secondAddressInput(e.target.value))}
                            }></input>
                        <input label="city" type="text" 
                            id="city" 
                            placeholder="City" 
                            value={city}
                            onChange={(e)=>
                                {dispatch(cityInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                    </div>
    
                    <div class="state-country">  
                        <input label="zipcode" type="text" 
                            id="zipcode"
                            placeholder="Zip" 
                            value={zipcode}
                            onChange={(e)=>
                                {dispatch(zipcodeInput(e.target.value));
                                dispatch(continueDietary())
                                }
                            }></input>
                        <button id="country" class="dropdown state-country-item">
                            {!country ? <a>Country</a> :
                            <a>{country}</a>}
                            <ul class="dropdown-content">
                                {Object.keys(countries).map((countryKey) => (
                                    <li key={countryKey} 
                                        onClick={()=>
                                            {dispatch(countryInput(countries[countryKey]));
                                            dispatch(continueDietary())
                                            }
                                        }><a>
                                    {countries[countryKey]}
                                    </a></li>
                                ))}
                            </ul>
                        </button>
                        <button id="state" class="dropdown state-country-item">
                            {!stateProvince ? <a>State/Province</a> :
                            <a>{stateProvince}</a>}
                            <ul class="dropdown-content menu bg-neutral rounded-box z-[1] overflow-y-scroll max-h-72">
                                {country === "United States"
                                ? Object.keys(usStates).map((usStateKey) => (
                                    <li key={usStateKey}
                                        onClick={()=>
                                            {dispatch(stateProvinceInput(usStates[usStateKey]));
                                            dispatch(continueDietary())
                                            }
                                        }><a>
                                    {usStates[usStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                country === "Mexico"
                                ? Object.keys(mxStates).map((mxStateKey) => (
                                    <li key={mxStateKey}
                                        onClick={()=>
                                            {dispatch(stateProvinceInput(mxStates[mxStateKey]));
                                            dispatch(continueDietary())
                                            }
                                        }><a>
                                    {mxStates[mxStateKey]}
                                    </a></li>
                                ))
                                : ( 
                                country === "Canada"
                                ? Object.keys(caStates).map((caStateKey) => (
                                    <li key={caStateKey} 
                                        onClick={()=>
                                            {dispatch(stateProvinceInput(caStates[caStateKey]));
                                            dispatch(continueDietary())
                                            }
                                        }><a>
                                    {caStates[caStateKey]}
                                    </a></li>
                                ))
                                : 
                                <li></li>
                                ))
                                }
                            </ul>
                        </button>
                    </div> 
                    <h2 id="contact-bottom">We will send you text and email confirmations!</h2>
                </div>
            </CardStackPage>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <NavLink className='btn-23' to='/rsvp' end><marquee>Return</marquee></NavLink> 
                <NavLink className='btn-23' 
                    // maybe theres something to having an onhover here dispatch the continueDietary?
                    disabled={!canContinueDietary}
                    to={!canContinueDietary ? '/rsvp/contact' : '/rsvp/dietary'} onClick={(e) => {
                        if (!canContinueDietary) {
                            e.preventDefault(); // Prevent navigation
                            notify(`Ah! Please make sure you fill out all the fields - pronouns, address, city, state, phone number and country code, etc.`);
                        }
                    }}
                    end><marquee>Continue</marquee></NavLink> 

            </CardStackFooter>
        </>
    );
  }


const pronouns_list = {
    ff: "she/ her",
    mm: "he/ him",
    nn: "they/ them",
    fn: "she/ they",
    mn: "he/ they"
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