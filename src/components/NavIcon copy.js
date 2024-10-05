import { useEffect, useState, useRef } from "react";
import '../App.css';
import navIconCircle from '../assets/nav_icon_circle.png';
import innerItem from '../assets/nav_icon_temp_button.png';

export function NavIcon({handleNavClick}) {


    return (
        <div class="header-nav">
            <img class="outer-circle" src={navIconCircle} ></img>
            <div class="inner-circle" onClick={handleNavClick}>
                btn
            </div>
            {/* <img class="inner-button" src={innerItem} onClick={handleNavClick} ></img> */}
        </div>
    )
} 