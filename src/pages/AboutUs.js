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
            <CardStackPage pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                    {/* <div class="absolute scale-75">
                        <img src={require('../assets/green_squiggle.png')} />
                    </div> */}
                <div>
                    <h1>Welcome to our website!</h1>
                    <p>Matthew and I met right before thanksgiving in 2021, on a Hinge date. 
                        We went to a gallery, and then we got a beer at Jackbar.
                        Ever since we have been inseparable - we have a cat named Gizmo and a beautiful colorful apartment.
                        </p>
                        <br></br>
                    <p>We worked really hard on this website, making it from scratch!</p>
                    <p>I am so exicted to get married you guys :) Shoot us an email if you have any questions or comments. I dont know what to put on this page!</p>
                    <div class="mt-10">
                        <ButtonMailTo label="Write us an e-mail!" mailto="mailto:mitzitler@gmail.com" />
                    </div>
                </div>
            </CardStackPage>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <NavLink className='btn-23' 
                    // disabled for x seconds after loading
                    // disabled={rsvpStatus === 'undecided' ? true : false} 
                    to='/info'
                    end><marquee>INFO → </marquee></NavLink>
            </CardStackFooter>
        </>
    )
}