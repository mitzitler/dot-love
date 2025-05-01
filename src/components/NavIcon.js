import '../App.css';

export function NavIcon({children}) {


    return (
        <div className="header-nav">
          <img className="outer-circle" src="https://cdn.mitzimatthew.love/nav_icon_circle.png" ></img>
            <div className="egg-container" >
                {children}
            </div>
        </div>
    )
}
