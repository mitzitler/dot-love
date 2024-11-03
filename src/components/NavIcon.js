import '../App.css';
import navIconCircle from '../assets/nav_icon_circle.png';

export function NavIcon({children}) {
    return (
        <div class="header-nav">
            <img class="outer-circle" src={navIconCircle} ></img>
            <div class="inner-circle" >
                {children}
            </div>
        </div>
    )
} 