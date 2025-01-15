import React from 'react';
import { RegistryPage } from '../components/RegistryPage';


export function Registry() {

    const pageMainColor = "blue" 
    const pageSection = "registry"

    return (
        <main className="section-content w-full flex-grow bg-pink-400/75 border-pink-500/50 border-2">
            <RegistryPage />
        </main>
    )
}