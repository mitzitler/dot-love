import { useEffect, useState } from "react";
import { NavIcon } from "./NavIcon.js";
import '../App.css';

export function GenericHeader() {

    return (
        <div class = "header-main">
            <span class = "header-side">
                I am the left side
            </span>
            <NavIcon/> 
            <span class = "header-side">
                I am the right side
            </span>
        </div>
    )

}