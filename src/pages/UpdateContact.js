import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { useGetUserQuery, useRegisterRSVPMutation } from '../services/gizmo.js';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../components/CardStackPage.js';
import { CardStackFooter } from '../components/CardStackFooter.js';
// TODO: update with dispatching?
import { firstNameInput, lastNameInput, pronounsInput, 
    phoneNumberCountryCodeInput, phoneNumberInput, emailInput,
    streetAddressInput, secondAddressInput, cityInput, zipcodeInput,
    countryInput, stateProvinceInput, continueDietary } from '../../features/guest/rsvpSlice';
import '../App.css';

export function UpdateContact() {

    const pageMainColor = "emerald" 
    const pageSecondaryColor = "amber" 
    const pageTertiaryColor = "lilac" 
    const pageSection = "update"

    // TODO: for option 1 input boxes
    const email = useSelector((state) => state.rsvp.email)

    // TODO: Redux to grab the login header from state to call this api

    // API Call - triggers only when loginHeader changes
        const { data, error, isLoading } = useGetUserQuery(loginHeader, {
            skip: !loginHeader, // Skip API call if header is null
        });
    
        useEffect(() => {
            if (data && data.code === 200) {
                setLoginSuccess(true);
                // dispatch(setLoginSuccessState())
                dispatch(setloginHeaderState(loginHeader))
                console.log("Gizmo login success, result:", data);
                notify(`Welcome, ${data.body.user.first}! Please scroll down`)
            }
            if (error) {
                console.error("Login API call failed:", error);
            }
        }, [data, error, dispatch, loginHeader]);
    
        // TODO: useRegisterRSVPMutation to write update function

    return (

        <>
        <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} >
            <NavLink className='btn-23' 
                to='/about'
                end><marquee>ABOUT US → </marquee></NavLink>
        </CardStackFooter>
        <CardStackPage class="card-stack" pageMainColor={pageMainColor} 
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}>
            <h1>Contact Info</h1>
            <div>
                <h3>This is what we know about you, ${data.body.user.first}!</h3>
                <span>Email: ${data.body.user.email} 
                    {/* option 1: same as original flow */}
                    {/* <input label="email" type="text" id="email" placeholder="Want to change?" 
                        value={email} onChange={(e)=> {dispatch(zipcodeInput(e.target.value))}}>
                        </input> */}
                    {/* option 2: now just input box and submit, with update event on submit*/}
                    <input label="email" type="text" id="email" placeholder="Want to change?" 
                        value={email}>
                        </input>
                    <button onClick={()=>handleUpdate(v=email, field="email")}>Submit!</button>
                </span>
            </div>
        </CardStackPage>
        <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
            pageTertiaryColor={pageTertiaryColor} pageSection={pageSection} >
        </CardStackPage>
        </>
    )
}
