import { useEffect, useState } from "react";
import { NavIcon } from "./NavIcon.js";
import '../App.css';

export function GenericHeader({handleNavClick, leftSide, rightSide}) {

    return (
        <div ref={div => (this.header = div)} class = "header-main">
            {/* i am as tall as the inside of the rotating circle (not the outside) */}
            <div class = "header-main2">
                <span class = "header-side" onClick={handleNavClick}>
                    {leftSide}
                    {/* i am as tall as the inner button */}
                </span>
                <NavIcon handleNavClick={handleNavClick} /> 
                <span class = "header-side">
                    {rightSide}
                    {/* i am as tall as the inner button */}
                </span>
            </div>
        </div>
    )

}