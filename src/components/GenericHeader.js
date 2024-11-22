import { NavIcon } from "./NavIcon.js";
import '../App.css';

export function GenericHeader({children}) {
    
    return (
      <div class = "header-main">
          <NavIcon>
            {children}
          </NavIcon>
      </div>
    )
}