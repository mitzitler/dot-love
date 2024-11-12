import '../../App.css';
import { NavLink } from 'react-router-dom';

export function RSVPFormSubmit({rsvpString, contactString, dietaryString, firstName, lastName, dispatch}) {

  return(
    <>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            <div class="rsvp">    

            <h1 class="pt-20">Does this all look right, {firstName}?</h1> 
            <div className="grid col-2">
                <p className='p-5'>{contactString}</p>
                <p className='p-5'>{dietaryString}</p>
            </div>

            </div>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
            <span className='button-container'>
                <NavLink className='next-btn' to='/dietary' end>Go back?</NavLink> 
                {/* this part needs to conditionally render the button based on guest code */}
                <button className='next-btn' 
                    onClick={()=>dispatch({type:"submitForm", payload:`${firstName} ${lastName}`})}>Submit!!</button>
                {/* <NavLink className='next-btn' to='/' end>Submit!!!</NavLink>  */}
            </span>
        </section>
    </>
    )
}