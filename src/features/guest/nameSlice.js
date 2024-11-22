import { createSlice } from '@reduxjs/toolkit'

const nameSlice = createSlice({
    name: 'name',
    initialState: {
        id: 0,
        rsvp: "ATTENDING",
        firstName: "Mitzi",
        lastName: "Zitler",
        pronouns: "she/her"
    },
    reducers: {
      nameAdded(state, action) {
        const name = action.payload
        state.entities[name.id] = name
      },
      nameRsvp(state, action) {
        const { rsvp, nameId } = action.payload
        state.entities[nameId].rsvp = rsvp
      },
      nameFirstName(state, action) {
        const { firstName, nameId } = action.payload
        state.entities[nameId].firstName = firstName
      },
      nameLastName(state, action) {
        const { lastName, nameId } = action.payload
        state.entities[nameId].lastName = lastName
      },
      namePronouns(state, action) {
        const { pronouns, nameId } = action.payload
        state.entities[nameId].pronouns = pronouns
      }
    }
  })
  
  export const { nameAdded, nameRsvp, nameFirstName, nameLastName, namePronouns } = nameSlice.actions
  
  export default nameSlice.reducer

// const initialRsvpNameState = {
//     name: [
//         {id: 0, 
//         rsvp: "ATTENDING", 
//         firstName: "Mitzi", 
//         lastName: "Zitler", 
//         pronouns: "she/her",
//         },

//         {id: 1, 
//         rsvp: "ATTENDING", 
//         firstName: "Matthew", 
//         lastName: "Saucedo", 
//         pronouns: "he/him",
//         }
//     ]
// }

// function nextGuestId(name) {
//     const maxId = name.reduce((maxId, name) => Math.max(name.id, maxId), -1)
//     return maxId + 1
// }

// export default function nameReducer(state = initialRsvpNameState, action) {
//     switch (action.type) {
//         case 'name/nameRsvped': {
//             return {
//                 ...state,
//                 name: [
//                     ...state.name,
//                     {
//                         id: nextGuestId(state.name),
//                         rsvp: action.payload, 
//                         firstName: "", lastName: "", pronouns: ""
//                     }
//                 ]
//             }
//         }

        // case 'name/nameFirstName': {
        //     return state.map(name => {
        //         if (name.id !== action.payload) {
        //             return name
        //         }

        //         return {
        //             ...name,
        //             firstName: firstName // action.text?
        //         }
        //     })
        // }

        // case 'name/nameLastName': {
        //     return state.map(name => {
        //         if (name.id !== action.payload) {
        //             return name
        //         }

        //         return {
        //             ...name,
        //             lastName: lastName // action.text?
        //         }
        //     })
        // }

        // case 'name/namePronouns': {
        //     return state.map(name => {
        //         if (name.id !== action.payload) {
        //             return name
        //         }

        //         return {
        //             ...name,
        //             pronouns: pronouns // action.text?
        //         }
        //     })
        // }

//         default:
//             return state
//     }
// }