import '../App.css';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

export function FormSubmitLeft() {

    const dispatch = useDispatch();

    const rsvpCode = useSelector((state) => state.rsvp.rsvpCode)
    const rsvpStatus = useSelector((state) => state.rsvp.rsvpStatus)

    const firstName = useSelector((state) => state.rsvp.firstName) 
    const lastName = useSelector((state) => state.rsvp.lastName)
    const pronouns = useSelector((state) => state.rsvp.pronouns)
    const phoneNumber = useSelector((state) => state.rsvp.phoneNumber)
    const email = useSelector((state) => state.rsvp.email)
    const streetAddress = useSelector((state) => state.rsvp.streetAddress)
    const secondAddress = useSelector((state) => state.rsvp.secondAddress)
    const city = useSelector((state) => state.rsvp.city)
    const zipcode = useSelector((state) => state.rsvp.zipcode)
    const country = useSelector((state) => state.rsvp.country)
    const stateProvince = useSelector((state) => state.rsvp.stateProvince)

    const name = firstName + " " + lastName

    const contactString = "Hi " + firstName + " " + lastName + " (" + pronouns + "), " +
    "we can reach you at " + phoneNumber + " or " + email + " and your mailing address is " + 
    streetAddress + " " + secondAddress + ", in " + city + ", " + zipcode + " - " + 
    stateProvince + ", " + country 

    const countryNew = country === "United States" ? "the US" : country

    return(
        <div className="submit-card-left">
            {/* i hate this styling so much */}
            <h3 className="submit-text-overlay ">
                Your mailing address is: {streetAddress} {city}, {stateProvince} {zipcode} - in  {countryNew}
            </h3>
            <p></p>
            <h3 className="submit-text-overlay">
                We will reach out to you at {phoneNumber} and {email}
            </h3>
        </div>
    )



}