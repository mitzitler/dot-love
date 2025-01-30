import '../App.css';

export function NavIcon({children}) {


    return (
        <div class="header-nav">
          <img class="outer-circle" src="https://cdn.mitzimatthew.love/nav_icon_circle.png" ></img>
            <div class="egg-container" >
                {children}
            </div>
        </div>
    )
}
