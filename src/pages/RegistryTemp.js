import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
import { useGetRegistryItemsQuery } from '../services/spectaculo.js';
import '../App.css';

export function RegistryTemp() {

    const pageMainColor = "cream" 
    const pageSecondaryColor = "plum" 
    const pageTertiaryColor = "terracotta" 
    const pageSection = "registry"

    let loginHeader = 'mitzi_zitler'

    // API Call - triggers only when loginHeader changes
    const { data } = useGetRegistryItemsQuery(loginHeader);

    console.log(data)
    // console.log(data.body)
    // console.log(data.body.items)

    return (

        <>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                to='/about'
                end><marquee>NAVIGATION → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}>

            <h1>Temp Registry Page</h1>


            </CardStackPage>
        </>
    )
}