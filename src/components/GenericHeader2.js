import { NavIcon } from "./NavIcon.js";
import React, {useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fullNameCodeInput } from '../features/guest/userSlice';
import '../App.css';

export function GenericHeader2({placeholder, entryValue, setEntryValue}) {

  // {placeholder, entryValue, setEntryValue, inputHandler}
  // this state defined in app
  // const [entryValue, setEntryValue] = useState("")

  const dispatch = useDispatch();
  const fullNameCode = useSelector((state) => state.user.fullNameCode) 

  const handleSubmit = (e) => {
    e.preventDefault()
  }

  const handleChange = (e) => {
    setEntryValue(e.target.value)
  }

  const handleClearField = (e) => {
    setEntryValue("")
  }
    
  const adjustFontSize = () => {
    let fontSize = 1;
    if (entryValue.length <= 10) {
      fontSize = fontSize*0.55
    } else {
      fontSize = fontSize*0.55 - (entryValue.length-10)*0.05
     }

    document.getElementById("genericheader2").style.fontSize = fontSize + 'em'
    console.log("font size: ", fontSize)
  } 

  useEffect(() => {
    adjustFontSize()
  }, [entryValue])

  // for rsvp, placeholder = "RSVP Code?
  // entryValue = rsvpCode // the variable
  // inputHandler = (e)=>dispatch(rsvpCodeInput(e.target.value))

    return (
      <div class = "header-main">
          <NavIcon>
            <div class= "egg backdrop-blur-xl" />
            <form  
            onSubmit={handleSubmit}>
              <input placeholder={placeholder} type="text"
                  id="genericheader2"
                  value={entryValue} // pattern="[A-Za-z]*"
                  onChange={handleChange}
                  onFocus={handleClearField}
                  onInput={(e)=>dispatch(fullNameCodeInput(e.target.value))}/>
            </form>
          </NavIcon>
      </div>
    )
}