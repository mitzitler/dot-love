import React, { useState, useEffect } from 'react';
import { GenericHeader } from '../components/GenericHeader';
import { Info } from './Info';
import { AboutUs } from './AboutUs';
import { Routes, Route } from 'react-router-dom';
import { useGetUserQuery } from '../services/gizmo.js';
import { toast } from 'react-toastify'; // Toast (yum!)
import '../App.css';

export function Home() {
    const [entryValue, setEntryValue] = useState("")
    const entryValuePlaceholder = "First Last"
    const [loginHeader, setLoginHeader] = useState(null);
    const [loginSuccess, setLoginSuccess] = useState(false);

    // Function to emit toast 🍞
    const notify = (input) => {
        toast.info(input, {
            theme: "dark",
            position: "top-right",
            icon: <img src='' style={{ paddingLeft: 16,  width: 30, height: 30 }} alt='💕' />
        })
    }

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

    const handleClearField = () => {
        setEntryValue("");
        setLoginHeader(null);
    };

    return (
        <>
        <GenericHeader classname="h-screen transfom-scale-5"
            placeholder={"Full name?"} entryValue={entryValue} 
            setEntryValue={setEntryValue}>
            <div class= "egg backdrop-blur-xl" />
            <form>
              <input placeholder={entryValuePlaceholder} type="text"
                  id="genericheader"
                  value={entryValue}
                  onFocus={handleClearField}
                  onInput={handleNameChange}/>
            </form>
        </GenericHeader>
        { loginSuccess ?
            <div classname="container">
                <main className="card-stack">

                    <Routes>
                        <Route path="/" element={<Info/>} />
                        <Route path="/info" element={<Info/>} />
                        <Route path="/aboutus" element={<AboutUs/>} />
                    </Routes>

                </main>
            </div>
        : <></>
        }
        </>
        
    )
}
