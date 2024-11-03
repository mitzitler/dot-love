import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { NavIcon } from "./NavIcon.js";
import '../App.css';

export function GenericHeader() {
    const [pageNum, setPageNum] = useState(1)
    const pageMax = 4
  
    function handleNavClick() {
      console.log('You clicked me')
      console.log(pageNum)
      if (pageNum < pageMax) {
        setPageNum(pageNum+1)
      } else {
        setPageNum(1)
      };
    }
    
    console.log(pageNum)

    // order is current_place: next_nav_link

    const router_order = {
        1: "/info",
        2: "/registry",
        3: "/about",
        4: "/data",
        5: "/"
    }
    
    return (
        <div class = "header-main">
                <NavIcon />
                {/* <NavLink // isActive is not useful here
                    className='px-4 block pt-3 pb-1 hover:bg-teal-600'
                      to={router_order[pageNum]}
                      onClick={
                        // console.log('hi', router_order[pageNum])
                        () => handleNavClick()
                    }
                      end>
                    Next
                </NavLink>  */}
        </div>
    )

}

// export function GenericHeader() {

//     return (
//         <div class = "header-main">
//             <div class = "header-main2">
//                 <NavIcon
//                     className={({ isActive }) =>
//                         'px-4 block pt-3 pb-1 hover:bg-teal-600' +
//                         (isActive ? ' bg-teal-600' : '')
//                       }
//                       to="/"
//                       end>
//                     RSVP
//                 </NavIcon> 
//                 <NavIcon
//                     className={({ isActive }) =>
//                         'px-4 block pt-3 pb-1 hover:bg-teal-600' +
//                         (isActive ? ' bg-teal-600' : '')
//                       }
//                       to="/info"
//                       end>
//                     Info
//                 </NavIcon> 
//                 <NavIcon
//                     className={({ isActive }) =>
//                         'px-4 block pt-3 pb-1 hover:bg-teal-600' +
//                         (isActive ? ' bg-teal-600' : '')
//                       }
//                       to="/registry"
//                       end>
//                     Registry
//                 </NavIcon> 
//                 <NavIcon
//                     className={({ isActive }) =>
//                         'px-4 block pt-3 pb-1 hover:bg-teal-600' +
//                         (isActive ? ' bg-teal-600' : '')
//                       }
//                       to="/about"
//                       end>
//                     About
//                 </NavIcon> 
//                 <NavIcon
//                     className={({ isActive }) =>
//                         'px-4 block pt-3 pb-1 hover:bg-teal-600' +
//                         (isActive ? ' bg-teal-600' : '')
//                       }
//                       to="/data"
//                       end>
//                     Data
//                 </NavIcon> 
//             </div>
//         </div>
//     )

// }