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

    // here i need to make a modified vers of registry items with price_cat
    // which filters out display = true
    // and adds a flag for certain brands

    console.log(registryItems)

    console.log(claimedItems)

    const categorizePrice = (price_cents) => {
        if (price_cents == 0) return '??'
        if (price_cents > 0 && price_cents <= 7500) return '$0-75';
        if (price_cents <= 15000) return '$75-150';
        if (price_cents <= 25000) return '$150-225';
        if (price_cents <= 30000) return '$225-300';
        if (price_cents > 30000) return '$300+';
        return '$300+'
    };
      
    let registryItemsCat = Object.fromEntries(
        Object.entries(registryItems)
            .filter(([_, value]) => value.display) 
            .map(([key, value]) => [
                key,
                { ...value, price_cat: categorizePrice(value.price_cents) },
        ])
    );

    registryItemsCat = Object.entries(registryItemsCat).map(([key, item]) => ({
        ...item,
        id: key,
      }));

    let claimedItemsFilter = Object.fromEntries(
        Object.entries(claimedItems)
            .filter(([_, value]) => value.claim_state == "CLAIMED")
    )

    let claimedItemsClaimed = Object.entries(claimedItemsFilter).map(([key, item]) => ({
        ...item,
        id: key,
      }));


    return (
    
        <>

        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                to='/about'
                end><marquee>ABOUT US → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryChartPage registryItems={registryItemsCat} />
        </CardStackPage>
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <RegistryTablePage registryItems={registryItemsCat} />
        </CardStackPage>

        { claimedItemsClaimed.length == 0 ? <></> :  
            <CardStackPage pageMainColor={pageMainColor} 
                pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
                pageSection={pageSection}>
                <RegistryClaimPage registryItems={registryItemsCat}  claimedItems={claimedItemsClaimed} />
            </CardStackPage>
        }

        </>
    )

}

