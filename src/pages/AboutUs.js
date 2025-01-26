import React from 'react';
import { useState, useCallback } from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import {AboutUsBody} from '../components/AboutUsBody.js'

export function AboutUs() {

    const pageMainColor = "lilac" 
    const pageSecondaryColor = "emerald"
    const pageTertiaryColor = "lime"
    const pageSection = "aboutus"

    return (

        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            {/* <div className={`section-content swipe-card flex-grow bg-lilac-400/75 border-lilac-500/50 border-2 backdrop-blur-md`}> */}
            <div>
                hi
            </div>
        </CardStackPage>
    )
}