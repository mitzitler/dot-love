import React from 'react';
import { useState, useCallback } from 'react';
import { CardStackPageClass } from '../components/CardStackPageClass.js';
import {AboutUsBody} from '../components/AboutUsBody.js'

export function AboutUs() {

    const pageMainColor = "pink" 
    const pageSecondaryColor = "emerald"
    const pageTertiaryColor = "babyblue"
    
    const pageMainClass = 'section-content swipe-card flex-grow bg-' + pageMainColor + '-400/75 border-' + pageMainColor + '-500/50 border-1 backdrop-blur-md'
    const pageSecondaryClass = 'section-content swipe-card flex-grow bg-' + pageSecondaryColor + '-400/75 border-' + pageSecondaryColor + '-500/50 border-1 backdrop-blur-md'
    const pageTertiaryClass = 'section-content swipe-card flex-grow bg-' + pageTertiaryColor + '-400/75 border-' + pageTertiaryColor + '-500/50 border-1 backdrop-blur-md'

    const pageSection = "aboutus"

    return (

        <CardStackPageClass pageMainClass={pageMainClass} 
            pageSecondaryClass={pageSecondaryClass} pageTertiaryClass={pageTertiaryClass} 
            pageSection={pageSection}>
            {/* <div className={`section-content swipe-card flex-grow bg-lilac-400/75 border-lilac-500/50 border-2 backdrop-blur-md`}> */}
            <div>
                <h1>Welcome to our website!</h1>
                <p>Matthew and I met right before thanksgiving in 2021, on a Hinge date. 
                    We went to a gallery, and then we got a beer at Jackbar.</p>
                    <br></br>
                <p>We worked really hard on this website, making it from scratch!</p>
            </div>
        </CardStackPageClass>
    )
}