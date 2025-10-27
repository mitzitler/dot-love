import React from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import ButtonMailTo from '../components/ButtonMailTo.js';

export function AboutUs() {

    const pageMainColor = "pink" 
    const pageSecondaryColor = "emerald"
    const pageTertiaryColor = "babyblue"
    
    const pageSection = "aboutus"

    return (
        <>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <NavLink className='btn-23'
                    to='/registry'
                    end><marquee>REGISTRY → </marquee></NavLink>
            </CardStackFooter>
            <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                <div>
                    <h1>About Us</h1>
                    <h2>Welcome to our website!</h2>
                    <p>Matthew and I met right before thanksgiving in 2021, on a Hinge date. 
                        We went to a gallery, and then we got a beer at Jackbar.
                    </p>
                    <br/>
                    <p>    
                    Ever since we have been inseparable - we have a cat named Gizmo and a beautiful colorful apartment.
                        </p>
                        <br/>
                    <p>We worked really hard on this website, making it from scratch!</p>
                    
                </div>
            </CardStackPage>
            <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                <div>
                    <h1>About Us</h1>
                    <h2>Welcome to our website!</h2>
                    <p>I am so exicted to get married you guys :) Shoot us an email if you have any questions or comments. I dont know what to put on this page!</p>
                    <div class="mt-10">
                        <ButtonMailTo label="Write us an e-mail!" mailto="mailto:mitzitler@gmail.com" />
                    </div>
                </div>
            </CardStackPage>
        </>
    )
}