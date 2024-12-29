import { createSlice } from '@reduxjs/toolkit'

const rsvpSlice = createSlice({
  name: "rsvp",
  initialState: {
    // could be 'ABC', 'DEF', 'GHI'
    // rsvpCode: localStorage.getItem("rsvpCode") || "", 
    rsvpCode: '',
    // 'undecided', 'attending', 'notattenting'
    rsvp: 'undecided', 
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
    submitted: null
  },
  reducers: {
    rsvpCodeInput(state, action) {
      const rsvpCode = action.payload
      state.entities[rsvpCode.id] = rsvpCode
    },
    rsvpInput(state, action) {
      const rsvp = action.payload
      state.entities[rsvp.id] = rsvp
    },
    firstNameInput(state, action) {
      const firstName = action.payload
      state.entities[firstName.id] = firstName
    },
    lastNameInput(state, action) {
      const lastName = action.payload
      state.entities[lastName.id] = lastName
    },
    pronounsInput(state, action) {
      const pronouns = action.payload
      state.entities[pronouns.id] = pronouns
    },
    phoneNumberInput(state, action) {
      const phoneNumber = action.payload
      state.entities[phoneNumber.id] = phoneNumber
    },
    emailInput(state, action) {
      const email = action.payload
      state.entities[email.id] = email
    },
    streetAddressInput(state, action) {
      const streetAddress = action.payload
      state.entities[streetAddress.id] = streetAddress
    },
    secondAddressInput(state, action) {
      const secondAddress = action.payload
      state.entities[secondAddress.id] = secondAddress
    },
    cityInput(state, action) {
      const city = action.payload
      state.entities[city.id] = city
    },
    zipcodeInput(state, action) {
      const zipcode = action.payload
      state.entities[zipcode.id] = zipcode
    },
    countryInput(state, action) {
      const country = action.payload
      state.entities[country.id] = country
    },
    stateProvinceInput(state, action) {
      const stateProvince = action.payload
      state.entities[stateProvince.id] = stateProvince
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
    drinkAlcoholToggle(state, action) {
      const drinkAlcohol = action.payload
      state.entities[drinkAlcohol.id] = drinkAlcohol
    },
    eatMeatToggle(state, action) {
      const eatMeat = action.payload
      state.entities[eatMeat.id] = eatMeat
    },
    eatDairyToggle(state, action) {
      const eatDairy = action.payload
      state.entities[eatDairy.id] = eatDairy
    },
    eatFishToggle(state, action) {
      const eatFish = action.payload
      state.entities[eatFish.id] = eatFish
    },
    eatShellfishToggle(state, action) {
      const eatShellfish = action.payload
      state.entities[eatShellfish.id] = eatShellfish
    },
    eatEggsToggle(state, action) {
      const eatEggs = action.payload
      state.entities[eatEggs.id] = eatEggs
    },
    eatGlutenToggle(state, action) {
      const eatGluten = action.payload
      state.entities[eatGluten.id] = eatGluten
    },
    eatPeanutsToggle(state, action) {
      const eatPeanuts = action.payload
      state.entities[eatPeanuts.id] = eatPeanuts
    },
    moreRestrictionsInput(state, action) {
      const moreRestrictions = action.payload
      state.entities[moreRestrictions.id] = moreRestrictions
    },
    // not sure how i feel about these tbh
    submitFormGC1(state, action) {
      const submitted = action.payload
      state.entities[submitted.id] = submitted
    },
    submitFormGC1_5(state, action) {
      const submitted = action.payload
      state.entities[submitted.id] = submitted
    },
    // does this work?
    submitFormGC2(state, action) {
      const submitted = action.payload
      const rsvpCode = state.entities[rsvpCode]
      state.entities[submitted.id] = submitted
      state.entities[rsvpCode.id] = 'ABC'
    }  
  }
})

export const { rsvpCodeInput, rsvpInput, firstNameInput, lastNameInput, pronounsInput, 
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