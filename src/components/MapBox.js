import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

// this code is direct from searching "how to use mapbpx to display a chosen business on a map in react web app"
// into google ai overview
// im curious how well it works
// would love to add in some custom styling to make the color overlay well

export function MapBox({business}) {
    const mapContainer = useRef(null);
    const [map, setMap] = useState(null);

    useEffect(() => {
        if (mapContainer.current && !map) {
        const newMap = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/streets-v11',
            center: business.coordinates, // Replace with your business coordinates
            zoom: 12, // Set the initial zoom level
        });

        newMap.on('load', () => {
            new mapboxgl.Marker({
            color: '#FF0000', // Set the color of the marker
            })
            .setLngLat(business.coordinates) // Set the marker coordinates
            .addTo(newMap);
        });

        setMap(newMap);
        }
    }, [map, business.coordinates]);

    return (
        <div ref={mapContainer} style={{ height: '400px' }} />
    );

}