import '../App.css';
import navIconCircle from '../assets/nav_icon_circle.png';
import { useEffect } from 'react';

export function NavIcon({children}) {


    return (
        <div class="header-nav">
            <img class="outer-circle" src={navIconCircle} ></img>
            <div class="egg-container" >
                {children}
                {/* <div class= "egg backdrop-blur-xl" /> */}
                {/* on input (e)=>dispatch({type: "inputRSVPCode": payload: e.target.value}) */}
                {/* <input placeholder="RSVP code?" */}
                {/* onInput={()=>console.log('hey')}/> */}
            </div>
        </div>
    )
} 