import React from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { NewRegistryPage } from './RegistryPages/NewRegistryPage.js';
import { RegistryTablePage } from './RegistryPages/RegistryTablePage.js';
import { RegistryClaim } from './RegistryPages/RegistryClaim.js';

export function Registry({registryItems}) {

    const pageMainColor = "khaki"  // temp colors
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "babyblue"

    const pageSection = "registry"

    

    return (
    
        <>

        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                // disabled for x seconds after loading
                // disabled={rsvpStatus === 'undecided' ? true : false} 
                to='/about'
                end><marquee>ABOUT US → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <NewRegistryPage registryItems={registryItems} />
        </CardStackPage>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryTablePage registryItems={registryItems} />
        </CardStackPage>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryClaim registryItems={registryItems} />
        </CardStackPage>
        </>
    )

}

