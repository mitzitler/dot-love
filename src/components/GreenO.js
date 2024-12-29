import React from "react";
import { useEffect, useRef } from "react";
import '../App.css';

export function GreenO({divPositiionX, divPositiionY}) {

    const divRef = useRef(null);

    useEffect(() => {
        if (divRef.current) {
            const { x, y } = divRef.current.getBoundingClientRect();
            console.log('Div position: ', { x, y });
        }
    }, [divPositiionX])

    console.log('green o')
    return(
        <div className='big-green-o' ref={divRef}
            style ={{
                position: 'absolute',
                left: divPositiionX - 20,
                top: divPositiionY,
                margin: 'auto',
                textAlign: 'center',
                justifyContent: 'center',    
                color: 'green'   
            }}>
            O
        </div>
    )
}