import React from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { RegistryChartPage } from './RegistryPages/RegistryChartPage.js';
import { RegistryTablePage } from './RegistryPages/RegistryTablePage.js';
// import { RegistryClaimPage } from './RegistryPages/RegistryClaimPage.js';
import useGetUserClaimsQuery from '../services/spectaculo.js'

export function Registry({ loginHeader, registryItems,  claimedItems }) {

    const pageMainColor = "khaki"  // temp colors
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "babyblue"

    const pageSection = "registry"

    // console.log(claimedItems)

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
            <RegistryChartPage loginHeader={loginHeader} registryItems={registryItems} />
        </CardStackPage>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryTablePage loginHeader={loginHeader} registryItems={registryItems} />
        </CardStackPage>

        {/* used to have conditional rendering on claimedItems.length == 0 */}
        {/* { claimedItems.length == 0 ? <></> :  */}
            {/* <CardStackPage pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                <RegistryClaimPage registryItems={registryItems}  claimedItems={registryItems} />
            </CardStackPage> */}
        {/* } */}

        </>
    )

}

