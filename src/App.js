import React, { useState } from 'react';
import { RSVP } from './pages/RSVP'
import { Home } from './pages/Home';
import { LightShow } from './components/LightShowVideo'
import { Routes, Route } from 'react-router-dom';
import { ToastContainer} from 'react-toastify'; // Toast (yum!)

export default function App() {

  const [loginHeader, setLoginHeader] = useState(null);

  return (
    <div id = "root">
      <LightShow/>
      {/* 🍞 Toast 🍞 */}
      <ToastContainer
          position="top-right"
          zIndex={9999}
          toastStyle={{}}/>
      <Routes>
        <Route path="rsvp/*" element={<RSVP/>} />
        <Route path="*" element={<Home loginHeader={loginHeader} setLoginHeader={setLoginHeader} />} />
      </Routes>
    </div>
  );
}

