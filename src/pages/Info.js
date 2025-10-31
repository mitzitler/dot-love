import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { InfoBox } from './InfoPages/InfoComponents/InfoBox.js';
import { InfoBoxExpanded } from './InfoPages/InfoComponents/InfoBoxExpanded.js';
import '../App.css';

export function Info() {

    const [expandedBox, setExpandedBox] = useState("")

    const pageMainColor = "babyblue" 
    const pageSecondaryColor = "lilac" 
    const pageTertiaryColor = "amber" 
    const pageSection = "info"

    const rehearsal = {}

    const deity = {
        name: 'Diety Events',
        coordinates: [40.68725385467351, -73.98617663587743], 
      };

    function onClickExpand(id) {
        console.log(id)
        setExpandedBox((current) => (current === id ? null : id)); // Toggle expansion
    }

    return (

        <>
        {/* perhaps something on click here renders a pop up suggesting desktop ? */}
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                // disabled for x seconds after loading
                // disabled={rsvpStatus === 'undecided' ? true : false} 
                to='/registry'
                end><marquee>REGISTRY → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}>
            <h1>Info</h1>
            <h2>Saucedo-Zitler Wedding, November 7th 2025 at Diety Events</h2>
            <div class="right-justify"> {/* this div right justifies a column thats 70% wide */}
                <div class="collapsable-boxes"> {/* this div creates a vertical flexbox */}

                    <InfoBox id="time" class="schedule" collapsable={false}>
                        <h4>Schedule</h4>
                        <ul>
                            <li class="text-sm text-left pl-5"><em><strong>Thursday, November 6th</strong></em></li>
                            {rehearsal ? <li class="text-sm text-left pl-1"> 6.30pm - Rehearsal Dinner at Juliette</li> : <></>}
                            <li class="text-sm text-left pl-1"> 10.00pm - Welcome Drink Night at 33 Spritzenhaus</li>
                            <li class="text-sm text-left pl-5"><em><strong>Friday, November 7th</strong></em></li>
                            <li class="text-sm text-left pl-1"> 6.30pm - Champaign Flutes at Deity</li>
                            <li class="text-sm text-left pl-1"> 7.00pm - Ceremony </li>
                            <li class="text-sm text-left pl-1.5"> 7.30pm - Cocktail Hour</li>
                            <li class="text-sm text-left pl-1.5"> 8.30pm - Dinner</li>
                            <li class="text-sm text-left pl-1.5"> 10.00pm - Dancing</li>
                            <li class="text-sm text-left pl-1.5"> 12.00am - Afters at Someday Bar</li>
                            <li class="text-sm text-left">12.00am - Afters</li>
                        </ul>
                    </InfoBox>

                    <InfoBox id="stay" class="lodging" collapsable={true} onClickExpand={onClickExpand} 
                        expandedBox={expandedBox}>
                        <h3>Where should I stay?</h3>
                    </InfoBox>
                        {expandedBox === "stay" && (
                            <InfoBoxExpanded>
                                <ul>
                                    <li>🟡 For locals.. the venue is close to the G and A/C lines at Hoyt-Shemerhorn</li>
                                </ul>
                                <ul>
                                    <li>🟡 For lodging near the venue, try
                                        <a href='https://www.ihg.com/evenhotels/hotels/us/en/brooklyn/bxyev/hoteldetail'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;the EVEN Hotel
                                        </a> by IHG on 46 Nevins St, 
                                        <a href='https://www.marriott.com/en-us/hotels/nycys-sheraton-brooklyn-new-york-hotel/overview/'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;Sheraton Brooklyn 
                                        </a> by Marriott on 228 Duffield St, and 
                                        <a href='https://www.guestreservations.com/the-baltic-hotel/booking?checkIn=11%2F06%2F2025&checkOut=11%2F08%2F2025&rooms=1&adults%5B1%5D=2&children%5B1%5D=0&currency=USD'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;The Baltic Hotel 
                                        </a> on 489 Baltic St
                                    </li>
                                    <li>🟡 For lodging near our apartment, try 
                                        <a href='https://www.thepodhotel.com/pod-bk'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;The POD Hotel
                                        </a> on 247 Metropolitan Ave,
                                        <a href='https://www.codahotels.com/rooms'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;CODA Williamsburg
                                        </a> on 160 N 12th St, and
                                        <a href='https://www.penny-hotel.com/?utm_source=local-listings&utm_medium=organic&utm_campaign=local-listings'
                                        class='underline italic font-extrabold text-indigo-600 py-2'>
                                        &nbsp;The Penny Hotel
                                        </a> on 288 N 8th St
                                    </li>
                                </ul>
                            </InfoBoxExpanded>
                        )}

                    <InfoBox id="wear" class="dress-code" collapsable={true} onClickExpand={onClickExpand}
                        expandedBox={expandedBox}>
                        <h3>What should I wear?</h3>
                    </InfoBox>
                        {expandedBox === "wear" && (
                            <InfoBoxExpanded>
                                <ul>
                                    <li>🟡 Dress code is cocktail</li>
                                    <li>🟡 Scroll below for more details!</li>
                                </ul>    

                                <div class="mt-4">
                                </div>

                            </InfoBoxExpanded>
                        )}
                    
                </div>
            </div>
            </CardStackPage>
            <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection} >
                <h1>Info: Dress Code</h1>
                <h2>Saucedo-Zitler Wedding, November 7th 2025 at Diety Events</h2>
                <div class="right-justify"> {/* this div right justifies a column thats 70% wide */}
                    <div class="collapsable-boxes"> {/* this div creates a vertical flexbox */}

                        <InfoBox collapsable={false}>
                            <h4>Notes on Attire..</h4>
                            <ul>
                                <li class="text-sm text-left">The dress code for our wedding will be <b>cocktail attire.</b></li>
                                <br/>
                                <li class="text-sm text-left mb-3">What does this mean? Cocktail sits in between formal and semi formal.</li>
                                <li class="text-sm text-left mb-3">
                                If you like to wear suits, please feel free to wear a suit or dress shirt. 
                                </li>
                                <li class="text-sm text-left mb-3">
                                If you rather wear dresses, a cocktail dress or dressy seperates are great. 
                                </li>
                                <li class="text-sm text-left mb-3">
                                And of course, pantsuits, jumpsuits and dressy separates of the same lengths are great too!
                                </li>
                                <li class="text-sm text-left mb-3">
                                For this time of year, we’d also recommend a coat, and there will be coat check at the venue!
                                </li>

                                {/* here : scroll for more info about BRIDES SIDE */}
                                

                            </ul>
                        </InfoBox>
                    </div>
                </div>
            </CardStackPage>

            {/* here: conditionally render another page with ATTIRE EXAMPLES */}
        </>
    )
}