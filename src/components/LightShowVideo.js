import '../App.css';
// import BgVideo from '../assets/video/trim_vid.mp4';

export function LightShow() {
    return(
        <video autoPlay loop muted className="bg-vid"> 
            <source src='cdn.mitzimatthew.love/trim_vid.mp4' type="video/mp4" />
            {/* <source src={BgVideo} type="video/mp4" /> */}
        </video>
    )
}