import React from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { RegistryChartPage } from './RegistryPages/RegistryChartPage.js';
import { RegistryTablePage } from './RegistryPages/RegistryTablePage.js';
import { RegistryClaimPage } from './RegistryPages/RegistryClaimPage.js';
import useGetUserClaimsQuery from '../services/spectaculo.js'

export function Registry({ registryItems,  claimedItems }) {

    const pageMainColor = "khaki"  // temp colors
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "babyblue"

    const pageSection = "registry"

    return (
    
        <>

        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23'
                to='/games/militsa'
                end><marquee>GAMES → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryChartPage registryItems={registryItems} />
        </CardStackPage>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryTablePage registryItems={registryItems} />
        </CardStackPage>

        { claimedItems.length == 0 ? <></> :  
            <CardStackPage pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                <RegistryClaimPage registryItems={registryItems}  claimedItems={claimedItems} />
            </CardStackPage>
        }

        </>
    )

}

