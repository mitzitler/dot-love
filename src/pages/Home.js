// import { HomePageRoutes } from '../routes/HomePageRoutes';
import React, { useState, useEffect } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { useDispatch, useSelector } from 'react-redux';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Info } from './Info.js';
import { AboutUs } from './AboutUs.js';
import { Registry } from './Registry.js';
import { useGetUserQuery } from '../services/gizmo.js';
import { toast } from 'react-toastify'; // Toast (yum!)
import '../App.css';

export function Home() {

    const dispatch = useDispatch();

    const [entryValue, setEntryValue] = useState("")
    const entryValuePlaceholder = "First Last"
    const [loginHeader, setLoginHeader] = useState(null);
    const [loginSuccess, setLoginSuccess] = useState(false);

    // const loginSuccess = useSelector((state) => state.user.loginSuccess)

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
            console.log("Gizmo login success, result:", data);
            notify(`Welcome, ${data.body.user.first}! Please scroll down`)
        }
        if (error) {
            console.error("Login API call failed:", error);
        }
    }, [data, error]);

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
          event.preventDefault()
        }
      };

    const handleNameChange = (e) => {
        const value = e.target.value;
        setEntryValue(value);

        const [first, last] = value.trim().split(" ");
        if(e.keyCode == 13){ 
            e.preventDefault();
         }

        if (first && last) {
            const firstLast = `${first}_${last}`;
            setLoginHeader({ 'X-First-Last': firstLast });
        } else {
            setLoginHeader(null); // Prevent invalid API calls
        }
    };

    return (
        <>
        {/* TODO: only letters can be accepted */}
        <GenericHeader classname="h-screen transfom-scale-5">
            <div class= "egg backdrop-blur-xl" />
            <form>
              <input placeholder={entryValuePlaceholder} type="text"
                     id="genericheader"
                  value={entryValue}
                  onInput={handleNameChange}
                  onKeyDown={handleKeyDown}
                  />
            </form>
        </GenericHeader>
         { loginSuccess ?
            <div classname="container">
                <main className="card-stack">

                    <Routes>
                        <Route path="/" element={<Info/>} />
                        <Route path="/info" element={<Info/>} />
                        <Route path="/aboutus" element={<AboutUs/>} />
                        <Route path="/registry" element={<Registry/>} />
                    </Routes>

                </main>
            </div>
         : <></>
           }
        </>
    )
}
