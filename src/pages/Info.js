import React from 'react';
import { useState } from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import { InfoBox } from '../components/InfoBox.js';
import { MapBox } from '../components/MapBox.js';
// import {Loader, LoaderOptions} from 'google-maps';

// const options: LoaderOptions = 'region';
// const loader = new Loader('my-api-key', options);

// const google = await loader.load();
// const map = new google.maps.Map(document.getElementById('map'), {
// center: {lat: 40.68724549962714, lng: -73.98622621879578}, 
// zoom: 8,
// })

export function Info() {

    const [expandedBox, setExpandedBox] = useState("")

    const pageMainColor = "indigo" 
    const pageSection = "info"

    const diety = {
        name: 'Diety Events',
        coordinates: [40.68725385467351, -73.98617663587743], 
      };

    function onClickExpand() {
        
    }

    return (
        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
            <h1>Info</h1>
            <h2>Saucedo-Zitler Wedding, November 7th 2025 at Diety Events</h2>
            <div class="right-justify"> {/* this div right justifies a column thats 70% wide */}
                <div class="collapsable-boxes"> {/* this div creates a vertical flexbox */}

                    <InfoBox class="schedule" collapsable={false}>
                        <h3></h3>
                    </InfoBox>

                    <InfoBox id="A" class="lodging" collapsable={true} onClickExpand={onClickExpand}>
                        <h3>Where should I stay?</h3>
                    </InfoBox>
                    
                    <InfoBox id="B" class="dress-code" collapsable={true} onClickExpand={onClickExpand}>
                        <h3>What should I wear?</h3>
                    </InfoBox>
                    
                    <InfoBox id="C" class="faq" collapsable={true} onClickExpand={onClickExpand}>
                        <h3>What else should I know?</h3>
                    </InfoBox>
                    
                    <InfoBox class="map" collapsable={false}>
                        <MapBox business={diety}/>
                    </InfoBox>

                </div>
            </div>
        </CardStackPage>
    )
}