import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { GenericHeader } from '../components/GenericHeader';
import { useGetUserQuery } from '../services/gizmo.js';
import { setloginHeaderState } from '../features/guest/extrasSlice.js';
import { toast } from 'react-toastify'; // Toast (yum!)
import { useLocation } from 'react-router-dom';
import '../App.css';

export function HeaderHome({loginSuccess, setLoginSuccess, loginHeader, setLoginHeader}) {

    const dispatch = useDispatch();

    // const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    const [entryValue, setEntryValue] = useState("")
    const entryValuePlaceholder = "First Last"

    // Function to emit toast 🍞
    const notify = (input) => {
        toast.info(input, {
            theme: "dark",
            position: "top-right",
            icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30 }} alt='💕' />
        })
    }

    const location = useLocation();
    useEffect(() => {
        window.scrollTo(0, 0); 
    }, [location.pathname]);

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

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
          event.preventDefault()
        }
      };

    const handleNameChange = (e) => {
        const value = e.target.value;
        setEntryValue(value);

        const [first, last] = value.trim().split(" ");
        const [first1, first2, last1] = value.trim().split(" ");

        if(e.keyCode == 13){
            e.preventDefault();
         }
      
         if (first1 && first2 && last1) {
            const firstLast = `${first1} ${first2}_${last1}`;
            console.log('first1 first2 and last: ', firstLast)
            setLoginHeader({ 'X-First-Last': firstLast})
        } else if (first && last) {
            const firstLast = `${first}_${last}`;
            console.log('first and last: ', firstLast)
            setLoginHeader({ 'X-First-Last': firstLast})
        } else {
            setLoginHeader(null); // Prevent invalid API calls
        }
        
    };

    return (
        <>
        {/* TODO: only letters can be accepted */}
        <GenericHeader className="h-screen transfom-scale-5"
            placeholder={"Full name?"} entryValue={entryValue} 
            setEntryValue={setEntryValue}>
            <div className= "egg backdrop-blur-xl" />
            <form>
              <input placeholder={entryValuePlaceholder} type="text"
                  id="genericheader"
                  value={entryValue}
                  onInput={handleNameChange}
                  onKeyDown={handleKeyDown}/>
            </form>
        </GenericHeader>
        </>
    )
}
