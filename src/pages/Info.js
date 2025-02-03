import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import { InfoBox } from '../components/InfoBox.js';
import { InfoBoxExpanded } from '../components/InfoBoxExpanded.js';
import '../App.css';

// import { MapBox } from '../components/MapBox.js'; // this doesnt work rn
// import {Loader, LoaderOptions} from 'google-maps';

// const options: LoaderOptions = 'region';
// const loader = new Loader('my-api-key', options);

// const google = await loader.load();
// const map = new google.maps.Map(document.getElementById('map'), {
// center: {lat: 40.68724549962714, lng: -73.98622621879578}, 
// zoom: 8,
// })

// look at this: https://blog.openreplay.com/creating-a-collapsible-component-for-react/

export function Info() {

    const [expandedBox, setExpandedBox] = useState("")
    // const [isExpanded, setIsExpanded] = useState(false)

    // const toggleIsExpanded = useCallback(() => {
    //     setIsExpanded((isExpanded) => !isExpanded);
    //   }, []);

    const pageMainColor = "babyblue" 
    const pageSecondaryColor = "lilac" 
    const pageTertiaryColor = "amber" 
    const pageSection = "info"
    
    // useEffect(() => {
    //     window.scrollTo(0, 0); 
    // }, []);

    const diety = {
        name: 'Diety Events',
        coordinates: [40.68725385467351, -73.98617663587743], 
      };

    function onClickExpand(id) {
        console.log(id)
        setExpandedBox((current) => (current === id ? null : id)); // Toggle expansion
    }

    // console.log(pageMainClass)

    return (

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
                                    <li>🟡 Dress code is semi-formal</li>
                                    <li>🟡 Wedding colors to come soon!!!</li>
                                    <li>🟡 Pinterest board to come soon!!!</li>
                                </ul>    
                            </InfoBoxExpanded>
                        )}
                    
                    <InfoBox id="faq" class="faq" collapsable={true} onClickExpand={onClickExpand}
                        expandedBox={expandedBox}>
                        <h3>What else should I know?</h3>
                    </InfoBox>
                        {expandedBox === "faq" && (
                            <InfoBoxExpanded>
                                <ul>
                                    <li>🟡 This venue has stairs, so please let us know as soon as you can if you have mobility issues</li>
                                    <li>🟡 We'll text whenever we have updates with more information!</li>
                                    <li></li>
                                </ul>
                            </InfoBoxExpanded>
                        )}
                    
                    {/* <InfoBox id="map" class="map" collapsable={false}> */}
                        {/* <MapBox business={diety}/> */}
                    {/* </InfoBox> */}

                </div>
            </div>
        </CardStackPage>
        // this card stack page is missing the top child, and puts the third child as a nav bar card
        // </>
    )
}