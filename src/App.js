import React, {useRef} from 'react';
import { RSVP } from './pages/RSVP'
import { Home } from './pages/Home';
import { LightShow } from './components/LightShowVideo'
import { Routes, Route } from 'react-router-dom';
import { ToastContainer} from 'react-toastify'; // Toast (yum!)

export default function App() {

  return (
    <div id = "root">
      <LightShow/>
      {/* 🍞 Toast 🍞 */}
      <ToastContainer
          position="top-right"
          toastStyle={{}}/>
      <Routes>
        <Route path="rsvp/*" element={<RSVP/>} />
        <Route path="*" element={<Home/>} />
      </Routes>
    </div>
  );
}

