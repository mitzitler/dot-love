import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { InfoBox } from '../components/InfoBox.js';
import { InfoBoxExpanded } from '../components/InfoBoxExpanded.js';
import '../App.css';

export function Info() {

    const [expandedBox, setExpandedBox] = useState("")

    const pageMainColor = "babyblue" 
    const pageSecondaryColor = "lilac" 
    const pageTertiaryColor = "amber" 
    const pageSection = "info"

    const diety = {
        name: 'Diety Events',
        coordinates: [40.68725385467351, -73.98617663587743], 
      };

    function onClickExpand(id) {
        console.log(id)
        setExpandedBox((current) => (current === id ? null : id)); // Toggle expansion
    }

    return (

        <>

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
                            <li class="text-sm text-left pl-1"> 6.30pm - Ceremony at Diety Events</li>
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
                                    {/* <li>🟡 Wedding colors to come soon!!!</li> */}
                                    {/* <li>🟡 Pinterest board to come soon!!!</li> */}
                                </ul>    

                                <div class="mt-4">
                                    <NavLink 
                                    to='/info/dresscode' end>
                                        <div class="px-4 py-2 m-auto w-40 text-center border-dashed border-4 bg-slate-200 border-red-300 font-mono">
                                            More on dress code!
                                        </div>
                                    </NavLink>
                                </div>

                            </InfoBoxExpanded>
                        )}
                    
                </div>
            </div>
            </CardStackPage>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <NavLink className='btn-23' 
                    // disabled for x seconds after loading
                    // disabled={rsvpStatus === 'undecided' ? true : false} 
                    to='/about'
                    end><marquee>ABOUT US → </marquee></NavLink>
            </CardStackFooter>
        </>
    )
}