import { useEffect, useState, useRef } from "react";
import '../App.css';
import navIconCircle from '../assets/nav_icon_circle.png';
import innerItem from '../assets/nav_icon_temp_button.png';

export function NavIcon() {


    return (

    <div class="header-nav">
        <img class="outer-circle" src={navIconCircle} ></img>
        <img class="inner-button" src={innerItem} ></img>
    </div>
    )
} 