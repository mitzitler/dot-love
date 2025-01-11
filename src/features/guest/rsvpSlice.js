import { createSlice } from '@reduxjs/toolkit'

const rsvpSlice = createSlice({
  name: "rsvp",
  initialState: {
    // could be 'ABC', 'DEF', 'GHI'
    // rsvpCode: localStorage.getItem("rsvpCode") || "", 
    rsvpCode: '',
    // 'undecided', 'attending', 'notattenting'
    rsvpStatus: 'undecided', 
    firstName: "", 
    lastName: "", 
    pronouns: "", 
    phoneNumber: "", 
    email: "", 
    streetAddress: "", 
    secondAddress: "", 
    city: "", 
    zipcode: "",    
    country: "", 
    stateProvince: "", 
    canContinueDietary: false,
    drinkAlcohol: true, 
    eatMeat: true, 
    eatDairy: true,
    eatFish: true, 
    eatShellfish: true, 
    eatEggs: true, 
    eatGluten: true, 
    eatPeanuts: true, 
    moreRestrictions: "",
    submitted: null,
    rsvpSubmission: "",
  },
  reducers: {
    rsvpCodeInput(state, action) {
      state.rsvpCode = action.payload
    },
    rsvpStatusInput(state, action) {
      state.rsvpStatus = action.payload
    },
    firstNameInput(state, action) {
      state.firstName = action.payload
    },
    lastNameInput(state, action) {
      state.lastName = action.payload
    },
    pronounsInput(state, action) {
      state.pronouns = action.payload
    },
    phoneNumberInput(state, action) {
      state.phoneNumber = action.payload
    },
    emailInput(state, action) {
      state.email = action.payload
    },
    streetAddressInput(state, action) {
      state.streetAddress = action.payload
    },
    secondAddressInput(state, action) {
      state.secondAddress = action.payload
    },
    cityInput(state, action) {
      state.city = action.payload
    },
    zipcodeInput(state, action) {
      state.zipcode = action.payload
    },
    countryInput(state, action) {
      state.country = action.payload
    },
    stateProvinceInput(state, action) {
      state.stateProvince = action.payload
    },
    continueDietary(state, action) {
    // is this okay?
      { 
        console.log("can i continue? ", state.canContinueDietary);
        if (!state.firstName || !state.lastName || !state.pronouns || 
          !state.phoneNumber || !state.email || !state.streetAddress || 
          !state.city || !state.zipcode || !state.country || !state.stateProvince)
      return {...state, canContinueDietary: false} 
      else return {...state, canContinueDietary: true}
     // only allow this action if the items on the page are ready
    };
    },
    drinkAlcoholToggle(state) {
      state.drinkAlcohol = !state.drinkAlcohol
    },
    eatMeatToggle(state) {
      state.eatMeat = !state.eatMeat
    },
    eatDairyToggle(state) {
      state.eatDairy = !state.eatDairy
    },
    eatFishToggle(state) {
      state.eatFish = !state.eatFish
    },
    eatShellfishToggle(state) {
      state.eatShellfish = !state.eatShellfish
    },
    eatEggsToggle(state) {
      state.eatEggs = !state.eatEggs
    },
    eatGlutenToggle(state) {
      state.eatGluten = !state.eatGluten
    },
    eatPeanutsToggle(state) {
      state.eatPeanuts = !state.eatPeanuts
    },
    moreRestrictionsInput(state, action) {
      state.moreRestrictions = action.payload
    },
    // not sure how i feel about these tbh
    submitFormGC1(state, action) {
      state.submitted = action.payload
      state.rsvpSubmission = {
        rsvp: state.rsvp
      }
    },
    submitFormGC1_5(state, action) {
      state.submitted = action.payload
      state.rsvpSubmission = {
        rsvpStatus: state.rsvpStatus,
        pair_first_last: action.payload
      }
    },
    // does this work?
    submitFormGC2(state, action) {
      state.submitted = action.payload
      state.rsvpCode = 'ABC'
      state.rsvpSubmission = {
        rsvpStatus: state.rsvpStatus,
        pair_first_last: action.payload
      }
    }  
  }
})

export const { rsvpCodeInput, rsvpStatusInput, firstNameInput, lastNameInput, pronounsInput, 
  phoneNumberInput, emailInput, streetAddressInput, secondAddressInput, cityInput, zipcodeInput, countryInput, stateProvinceInput,
  continueDietary, drinkAlcoholToggle, eatMeatToggle, eatDairyToggle, eatFishToggle, eatShellfishToggle,
  eatEggsToggle, eatGlutenToggle, eatPeanutsToggle, moreRestrictionsInput,
  submitFormGC1, submitFormGC1_5, submitFormGC2 } = rsvpSlice.actions
  
export default rsvpSlice.reducer

// function reducer(state, action) {
//   switch (action.type) {
//       case "rsvpCodeInput": 
//           localStorage.setItem("rsvpCode", action.payload);
//           return {
//               ...state, 
//               rsvpCode: action.payload
//           }
//       case "rsvpInput": 
//           return {
//               ...state, 
//               rsvp: action.payload
//           };

//       // case "continueContact": // this one isnt necessary
//       //     return { // only allow this action if the items on the page are ready
//       //     };
      
//       case "firstNameInput": return {...state, firstName: action.payload};
//       case "lastNameInput": return {...state, lastName: action.payload};
//       case "pronounsInput": return {...state, pronouns: action.payload};
//       case "phoneNumberInput": return {...state, phoneNumber: action.payload};
//       case "emailInput": return {...state, email: action.payload};
//       case "streetAddressInput": return {...state, streetAddress: action.payload};
//       case "secondAddressInput": return {...state, secondAddress: action.payload};
//       case "cityInput": return {...state, city: action.payload};
//       case "zipcodeInput": return {...state, zipcode: action.payload};
//       case "countryInput": return {...state, country: action.payload};
//       case "stateProvinceInput": return {...state, stateProvince: action.payload};

//       case "continueDietary": // but im not going to check for secondaddress
//           { 
//               console.log("can i continue? ", state.canContinueDietary);
//               if (!state.firstName || !state.lastName || !state.pronouns || 
//                 !state.phoneNumber || !state.email || !state.streetAddress || 
//                 !state.city || !state.zipcode || !state.country || !state.stateProvince)
//             return {...state, canContinueDietary: false} 
//             else return {...state, canContinueDietary: true}
//            // only allow this action if the items on the page are ready
//           };
      
//       case "drinkAlcoholToggle": return {...state, drinkAlcohol: !state.drinkAlcohol};
//       case "eatMeatToggle": return {...state, eatMeat: !state.eatMeat};
//       case "eatDairyToggle": return {...state, eatDairy: !state.eatDairy};
//       case "eatFishToggle": return {...state, eatFish: !state.eatFish};
//       case "eatShellfishToggle": return {...state, eatShellfish: !state.eatShellfish};
//       case "eatEggsToggle": return {...state, eatEggs: !state.eatEggs};
//       case "eatGlutenToggle": return {...state, eatGluten: !state.eatGluten};
//       case "eatPeanutsToggle": return {...state, eatPeanuts: !state.eatPeanuts};
//       case "moreRestrictionsInput": return {...state, moreRestrictions: action.payload};

//       case "submitFormGC1": return {...state, submitted: action.payload};
//       case "submitFormGC1.5": return {...state, submitted: action.payload};
//       case "submitFormGC2": return {...state, submitted: action.payload, rsvpCode: 'ABC' }
      
//       default: throw new Error("what did you do????")
//   }
// }


// const nameSlice = createSlice({
//     name: 'name',
//     initialState: {
//         id: 0,
//         rsvp: "ATTENDING",
//         firstName: "Mitzi",
//         lastName: "Zitler",
//         pronouns: "she/her"
//     },
//     reducers: {
//       nameAdded(state, action) {
//         const name = action.payload
//         state.entities[name.id] = name
//       },
//       nameRsvp(state, action) {
//         const { rsvp, nameId } = action.payload
//         state.entities[nameId].rsvp = rsvp
//       },
//       nameFirstName(state, action) {
//         const { firstName, nameId } = action.payload
//         state.entities[nameId].firstName = firstName
//       },
//       nameLastName(state, action) {
//         const { lastName, nameId } = action.payload
//         state.entities[nameId].lastName = lastName
//       },
//       namePronouns(state, action) {
//         const { pronouns, nameId } = action.payload
//         state.entities[nameId].pronouns = pronouns
//       }
//     }
//   })
  
//   export const { nameAdded, nameRsvp, nameFirstName, nameLastName, namePronouns } = nameSlice.actions
  
//   export default nameSlice.reducer

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