import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import '../App.css';

export function RegistryTemp({registryItems}) {

    const pageMainColor = "lilac" 
    const pageSecondaryColor = "babyblue" 
    const pageTertiaryColor = "raspberry" 
    const pageSection = "registry"

    console.log('prop drilled the reg items: ', registryItems)

    return (

        <>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                to='/about'
                end><marquee>NAVIGATION → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage className="card-stack" pageMainColor={pageMainColor} 
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}>

            <h1 className='py-4'>Temp Registry Page</h1>

                <ul>
                    {registryItems.map((item) => (
                        <li key={item.item_id}>
                            {item.name}
                        </li>
                    ))}
                </ul>

            </CardStackPage>
        </>
    )
}