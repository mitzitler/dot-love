// import { combineReducers  } from "redux";
import nameReducer from "./features/guest/nameSlice";

export default function rootReducer(state = {}, action) {

    return {
        name: nameReducer(state.name, action)
        // , contact
        // , diet
    }
}


// {type: 'name/nameRsvped', payload: rsvp}
// {type: 'name/nameFirstName', payload: firstName}
// {type: 'name/nameLastName', payload: lastName}
// {type: 'name/namePronouns', payload: pronouns}