import React from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../../components/CardStackPage.js';
import { CardStackFooter } from '../../components/CardStackFooter.js';
import { InfoBox } from '../../components/InfoBox.js';
import '../../App.css';

export function InfoDressCode(guestDressCode) {

    const pageMainColor = "babyblue" 
    const pageSecondaryColor = "lilac" 
    const pageTertiaryColor = "amber" 
    const pageSection = "info"

    const guestType = "bridesperson"

    // const guestType = ""

    return (

        <>

        <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}>
            <h1>Info</h1>
            {/* <h2>Saucedo-Zitler Wedding, November 7th 2025 at Diety Events</h2> */}
            <div >
            <NavLink 
            to='/info' end>
                <div class="px-4 py-2 m-auto w-40 text-center border-dashed border-4 bg-slate-200 border-red-300 font-mono">
                    Go up to the main page!
                </div>
            </NavLink>
            </div>

            <div class="left-justify mt-4 ml-10"> {/*  this div right justifies a column thats 70% wide left-justify mt-4 ml-10 */}
                <div class="collapsable-boxes"> {/* this div creates a vertical flexbox */}

                    <InfoBox id="more" class="schedule" collapsable={false}>
                        <h3 class="text-center">What should I wear?</h3>
                        <ul>
                            <br/>
                            <li class="text-sm text-left">The dress code for our wedding will be <b>cocktail attire.</b></li>
                            <br/>
                            <li class="text-sm text-left">What does this mean? Cocktail sits in between formal and semi formal.</li>
                            <li class="text-sm text-left">
                                    If you like to wear suits, please feel free to wear a suit or dress shirt. 
                                    If you rather wear dresses, a cocktail dress or dressy seperates are great. 
                                    And of course, pantsuits, jumpsuits and dressy separates of the same lengths are great too!
                                    For this time of year, we’d also recommend a coat, and there will be coat check at the venue!
                            </li>
                            {guestType === "bridesperson" ?
                            <>
                                <br/>
                                <div class="grid grid-cols-4">
                                    <div class="text-sm text-left grid col-span-3">
                                        {/* {guestDressCode[guestType]} */}
                                        We ask that bride's side wears from this list: x x x x x or similar style in this color.
                                    </div>
                                    <div class="grid col-span-1 w-10 h-10 m-auto rounded-full bg-terracotta-500" />
                                </div>
                            </> : <></>}
                        </ul>
                    </InfoBox>

                </div>
            </div>
            </CardStackPage>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
            </CardStackFooter>
        </>
    )
}


const guestDressCode = {
    'bridesPerson' : "If you are in the wedding party the bride's side, we ask that you wear this shade of pink, in midi-dress (idealy one of these styles from JJ's x x x x) ",
    'groomsPerson' : '',
    'closeFamily' : ''
}