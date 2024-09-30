import { useState, useEffect } from "react";
import { GenericHeader } from "./GenericHeader";
import { GenericBody } from "./GenericBody";
import '../App.css';

export function GenericPage({handleNavClick, leftSide, rightSide, body}) {
    
    return (
        <div>
            <GenericHeader handleNavClick={handleNavClick} leftSide={leftSide} rightSide={rightSide} />
            {/* <GenericBody body={body}/> */}
        </div>
    )
}
