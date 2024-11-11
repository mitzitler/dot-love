import '../../App.css';
import { NavLink } from 'react-router-dom';

export function RSVPFormSubmit({rsvpString, contactString, dietaryString, firstName, lastName, dispatch}) {

  return(
    <>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md">
            <div class="rsvp">    

            <h1 class="pt-20">Does this all look right?</h1> 



            <span>
                <NavLink className='next-btn' to='/dietary' end>Go back?</NavLink> 
                {/* this part needs to conditionally render the button based on guest code */}
                <button className='next-btn' 
                    onClick={()=>dispatch({type:"submitForm", payload:`${firstName} ${lastName}`})}>Submit!!</button>
                {/* <NavLink className='next-btn' to='/' end>Submit!!!</NavLink>  */}
            </span>

            </div>
        </section>
        <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
    </>
    )
}