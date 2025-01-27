import React from 'react';
import { CardStackPage } from '../components/CardStackPage.js';

export function AboutUs() {

    const pageMainColor = "pink" 
    const pageSecondaryColor = "emerald"
    const pageTertiaryColor = "babyblue"
    
    const pageSection = "aboutus"

    return (

        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <div>
                <h1>Welcome to our website!</h1>
                <p>Matthew and I met right before thanksgiving in 2021, on a Hinge date. 
                    We went to a gallery, and then we got a beer at Jackbar.</p>
                    <br></br>
                <p>We worked really hard on this website, making it from scratch!</p>
            </div>
        </CardStackPage>
    )
}