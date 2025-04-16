// import { HomePageRoutes } from '../routes/HomePageRoutes';
import React, { useState, useEffect } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { useGetUserQuery } from '../services/gizmo.js';
import { toast } from 'react-toastify'; // Toast (yum!)
import { loginSuccessInput } from '../features/guest/userSlice.js';
import { useLocation } from 'react-router-dom';
import '../App.css';
import { useSelector } from 'react-redux';

export function HeaderHome() {
    const [entryValue, setEntryValue] = useState("")
    const entryValuePlaceholder = "First Last"
    const [loginHeader, setLoginHeader] = useState(null);
    // const [loginSuccess, setLoginSuccess] = useState(false);

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
            loginSuccessInput(true);
            console.log("Gizmo login success, result:", data);
            notify(`Welcome, ${data.body.user.first}! Please scroll down`)
        }
        if (error) {
            console.error("Login API call failed:", error);
        }
    }, [data, error]);

    const handleNameChange = (e) => {
        const value = e.target.value;
        setEntryValue(value);

        const [first, last] = value.trim().split(" ");
        if (first && last) {
            const firstLast = `${first}_${last}`;
            setLoginHeader({ 'X-First-Last': firstLast });
        } else {
            setLoginHeader(null); // Prevent invalid API calls
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
          event.preventDefault()
        }
      };

    const handleClearField = () => {
        setEntryValue("");
        setLoginHeader(null);
    };

    const loginSuccess = useSelector((state) => state.user.loginSuccess) 

    // useEffect(() => {
    //     const preventScroll = (event) => {
    //       event.preventDefault();
    //     };
    
    //     if (!loginSuccess) {
    //       window.addEventListener("wheel", preventScroll, { passive: false });
    //       window.addEventListener("touchmove", preventScroll, { passive: false });
    //       window.addEventListener("keydown", (event) => {
    //         if (["ArrowUp", "ArrowDown", "Space", "PageUp", "PageDown"].includes(event.key)) {
    //           preventScroll(event);
    //         }
    //       });
    //     } else {
    //       window.removeEventListener("wheel", preventScroll);
    //       window.removeEventListener("touchmove", preventScroll);
    //       window.removeEventListener("keydown", preventScroll);
    //     }
    
    //     return () => {
    //       window.removeEventListener("wheel", preventScroll);
    //       window.removeEventListener("touchmove", preventScroll);
    //       window.removeEventListener("keydown", preventScroll);
    //     };
    //   }, [loginSuccess]);

    return (
        <>
        {/* TODO: only letters can be accepted */}
        <GenericHeader classname="h-screen transfom-scale-5"
            placeholder={"Full name?"} entryValue={entryValue} 
            setEntryValue={setEntryValue}>
            <div class= "egg backdrop-blur-xl" />
            <form>
              <input placeholder={entryValuePlaceholder} type="text"
                  id="genericheader"
                  value={entryValue}
                  onFocus={handleClearField}
                  onInput={handleNameChange}
                  onKeyDown={handleKeyDown}/>
            </form>
        </GenericHeader>
        </>
    )
}