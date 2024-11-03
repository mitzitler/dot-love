import '../App.css';
import BgVideo from '../assets/video/temp_60s_light_show.mov';

export function LightShow() {
    return(
        <video autoPlay loop muted className="bg-vid"> 
            <source src={BgVideo} type="video/mp4" />
        </video>
    )
}