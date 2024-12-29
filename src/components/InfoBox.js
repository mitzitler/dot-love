import React from "react";

export function InfoBox({children, collapsable, onClickExpand}) {

    // onclick expand button, this 

    const selected = false

    if (!collapsable) {
        return(
            <div class='info-box'>
                <p class='info-box-p'>{children}</p>
            </div> 
        )
    } else if (collapsable && !selected) { {/* InfoBoxExpanded will be the component that displays when its selected, and that will live on the Info.js page */}
        return(
            <div class='info-box'>
                <span> 
                    <button class='info-box-button' onClick={() => onClickExpand()}>+</button>
                    <p class='info-box-p'>{children}</p> 
                </span>
            </div>
        )
    } else if (collapsable && selected) {
        return(
            <div class='info-box'>
                <span> 
                    <button class='info-box-button' onClick={() => onClickExpand()}>V</button>
                    <p class='info-box-p'>{children}</p> 
                </span>
            </div>
        ) 
    } else {
        return(
            <div>
                Error!!
            </div>
        )
    }

}