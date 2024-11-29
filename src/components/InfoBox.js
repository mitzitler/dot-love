import React from "react";

export function InfoBox({children, collapsable, onClickExpand}) {

    // onclick expand button, this 

    if (!collapsable) {
        return(
            <div>
                {children}
            </div> 
        )
    } else if (collapsable) {
        return(
            <div>
                <span> 
                    <p>{children}</p> {/* left justify */}
                    <button onClick={() => onClickExpand()}>+</button> {/* right justify */}
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