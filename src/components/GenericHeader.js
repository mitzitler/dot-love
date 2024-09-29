import { useEffect, useState } from "react";
import { NavIcon } from "./NavIcon.js";
import '../App.css';

export function GenericHeader() {

    return (
        <div class = "header-main">
            {/* i am as tall as the inside of the rotating circle (not the outside) */}
            <span class = "header-side">
                I am the left side
                {/* i am as tall as the inner button */}
            </span>
            <NavIcon/> 
            <span class = "header-side">
                I am the right side
                {/* i am as tall as the inner button */}
            </span>
        </div>
    )

}