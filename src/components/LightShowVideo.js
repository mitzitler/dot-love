import '../App.css';

export function LightShow() {
    return(
        <video autoPlay loop muted playsInline className="bg-vid">
            <source src='https://cdn.mitzimatthew.love/trim_vid.mp4' type="video/mp4" />
        </video>
    )
}
