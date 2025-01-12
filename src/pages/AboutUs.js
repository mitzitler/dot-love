import React from 'react';
import { useState, useCallback } from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import {AboutUsBody} from '../components/AboutUsBody.js'

export function AboutUs() {

    // indigo, amber, teal, pink
    const pageMainColor = "pink" 
    const pageSection = "aboutus"

    return (

        <CardStackPage pageMainColor={pageMainColor} pageSection={pageSection}>
            <div>
                hi
            </div>
        </CardStackPage>
    )
}