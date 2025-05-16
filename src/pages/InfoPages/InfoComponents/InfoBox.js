import React from "react";

export function InfoBox({children, collapsable, onClickExpand, id, expandedBox}) {
    if (!collapsable) {
        return(
            <div class='info-box'>
                <p class='info-box-p'>{children}</p>
            </div> 
        )
    } else if (collapsable) { {/* InfoBoxExpanded will be the component that displays when its selected, and that will live on the Info.js page */}
        return(
            <div class='info-box' onClick={() => onClickExpand(id)}>
                <span> 
                    <button class='info-box-button' >
                        {/* i am getting slightly frustrated that the spacing jumps when the button is clicked lol */}
                        {expandedBox === id ? '-' : '+'}
                    </button>
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
