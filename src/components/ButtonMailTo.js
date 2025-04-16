import react from "react"
import { Link } from "react-router-dom"

const ButtonMailTo = ({ mailto, label }) => {
    return (
            <Link class="px-4 py-2 border-dashed border-4 bg-slate-200 border-red-300 font-mono"
                to='#'
                onClick={(e) => {
                    window.location.href = mailto;
                    e.preventDefault();
                }}
            >
                {label}
            </Link>
    )   
}

export default ButtonMailTo