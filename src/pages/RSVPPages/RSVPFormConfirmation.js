import React from 'react';
import { NavLink } from 'react-router-dom';
import '../../App.css';
import { CardStackPageClass } from '../../components/CardStackPageClass';
import { CardStackPage } from '../../components/CardStackPage';

export function RSVPFormConfirmation({pageMainColor, pageSecondaryColor, pageTertiaryColor, pageSection, rsvpCode}) {

    return (
        <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>

                <h1>RSVP Submission Confirmed!</h1>
                <div>
                    <h2>Thank you for RSVPing, your response has been registered!</h2>
                    <p>The button below will direct you to our main site:</p> 
                    <p><em><b>www.mitzimatthew.love</b></em></p>
                    <p>Log into the site from here on by typing in your full name (as on your RSVP). Then scroll to see our site!</p>
                    <p>Our site will give you the directions, the schedule, the dress code - and even has the registry.</p>
                    <p>We will be updating this main site over the next few weeks, so check back regularly!</p>
                </div>

                {/* for some reason this routes at the same position, not to the top */}
                {/* there are a million responses here: https://stackoverflow.com/questions/36904185/react-router-scroll-to-top-on-every-transition */}
                <NavLink to='/'>
                    <button class="btn-generic">On to the main site!</button>
                </NavLink>

        </CardStackPage>
    )
}