import React from "react";
import { useEffect, useRef } from "react";
import '../App.css';

// export function RedX({divPositiionX, divPositiionY}) {

//     const divRef = useRef(null);

//     useEffect(() => {
//         if (divRef.current) {
//             const { x, y } = divRef.current.getBoundingClientRect();
//             console.log('Div position: ', { x, y });
//         }
//     }, [divPositiionX])

//     console.log('red x')
//     return(
//         <div className='big-red-x' ref={divRef}
//             style ={{
//                 position: 'absolute',
//                 left: divPositiionX - 20,
//                 top: divPositiionY,
//                 margin: 'auto',
//                 textAlign: 'center',
//                 justifyContent: 'center',       
//             }}>
//             ❌
//         </div>
//     )
// }

export const RedX = ({ divPositionX, divPositionY, onAnimationEnd }) => {
    useEffect(() => {
      const timer = setTimeout(() => {
        onAnimationEnd();
      }, 1000); // Match animation duration
      return () => clearTimeout(timer);
    }, [onAnimationEnd]);
  
    return (
      <div
        className="big-red-x"
        style={{ left: divPositionX, top: divPositionY }}
      >
        ❌
      </div>
    );
  };