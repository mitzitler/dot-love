import React from 'react';
import { useState, useCallback } from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import { InfoBox } from '../components/InfoBox.js';
import { InfoBoxExpanded } from '../components/InfoBoxExpanded.js';

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

    const pageMainColor = "indigo" 
    const pageSection = "info"

    const diety = {
        name: 'Diety Events',
        coordinates: [40.68725385467351, -73.98617663587743], 
      };

    function onClickExpand(id) {
        console.log(id)
        setExpandedBox((current) => (current === id ? null : id)); // Toggle expansion
    }

    console.log(expandedBox)

    return (

        // but the header is specifcally for the 

        // <>
        // <GenericHeader classname="h-screen transfom-scale-5">

        //     <div class= "egg backdrop-blur-xl" />
        //     <input placeholder="RSVP code?"
        //         onInput={(e)=>dispatch({type: "rsvpCodeInput", payload: e.target.value})}/>

        // </GenericHeader>

        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
            <h1>Info</h1>
            <h2>Saucedo-Zitler Wedding, November 7th 2025 at Diety Events</h2>
            <div class="right-justify"> {/* this div right justifies a column thats 70% wide */}
                <div class="collapsable-boxes"> {/* this div creates a vertical flexbox */}

                    <InfoBox id="time" class="schedule" collapsable={false}>
                        <h4>Schedule</h4>
                        <ul>
                            <li class="text-sm">Nov 7th 6.30pm - Ceremony at Diety Events</li>
                            {/* <li>7.00pm - Drinks</li>
                            <li>8.00pm - Dinner</li>
                            <li>9.00pm - Dancing</li>
                            <li>11.59pm - Afters</li> */}
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
                                    <li>🟡 We ask that you stay in this palette</li>
                                    <li>🟡 More guidelines, as well as a pinterest board, are here</li>
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