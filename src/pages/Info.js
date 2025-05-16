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
                            <li class="text-sm text-left pl-5"><em><strong>Friday, November 7th</strong></em></li>
                            <li class="text-sm text-left pl-1"> 6.30pm - Ceremony at Deity Events</li>
                            <li class="text-sm text-left pl-1.5"> 7.00pm - Drinks</li>
                            <li class="text-sm text-left pl-1.5"> 8.00pm - Dinner</li>
                            <li class="text-sm text-left pl-1.5"> 9.00pm - Dancing</li>
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
                                    <li>🟡 We will announce hotels in the downtown Brooklyn area</li>
                                    <li>🟡 The venue is close to the G and A/C lines at Hoyt-Shemerhorn</li>
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