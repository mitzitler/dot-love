import React from 'react';
import { CardStackPage } from '../components/CardStackPage.js';
import { NewRegistryPage } from '../components/NewRegistryPage.tsx';


export function Registry() {

    const pageMainColor = "khaki"  // temp colors
    const pageSecondaryColor = "lime"
    const pageTertiaryColor = "babyblue"

    const pageSection = "registry"

    return (
    
        <CardStackPage pageMainColor={pageMainColor} 
            pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} 
            pageSection={pageSection}>
            <NewRegistryPage />
        </CardStackPage>
    )

}

