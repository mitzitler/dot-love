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
    phoneNumberCountryCode: "1",
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
    dateLinkRequested: false,
    rsvpSubmission: "",
    guestCode: ''
  },
  reducers: {
    rsvpCodeInput(state, action) {
      state.rsvpCode = action.payload
    },
    guestCodeInput(state, action) {
      state.guestCode = action.payload
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
    phoneNumberCountryCodeInput(state, action) {
      state.phoneNumberCountryCode = action.payload
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
      console.log("can i continue? ", state.canContinueDietary);
      const isPhoneValid = state.phoneNumber.length === 10;
      const isCountryCodeValid = state.phoneNumberCountryCode === 1 || 
                                 (state.phoneNumberCountryCode?.toString().length <= 2);
      if (!state.firstName || 
          !state.lastName || 
          !state.pronouns || 
          !isPhoneValid || 
          !state.email || 
          !state.streetAddress || 
          !state.city || 
          !state.zipcode || 
          !state.country || 
          !state.stateProvince || 
          !isCountryCodeValid)
      return {...state, canContinueDietary: false} 
      else return {...state, canContinueDietary: true}
     // only allow this action if the items on the page are ready
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
    dateLinkRequestedInput(state) {
      state.dateLinkRequested = !state.dateLinkRequested
    },
    // not sure how i feel about these tbh
    submitFormGC1(state, action) {
      state.submitted = action.payload
      state.rsvpSubmission = {
        rsvp: state.rsvp
      }
    },
    submitFormGC1_5(state, action) {
      state.submitted = action.payload[0]
      state.dateLinkRequested = action.payload[1]
      state.rsvpSubmission = {
        rsvpStatus: state.rsvpStatus,
        pair_first_last: action.payload
      }
    },
    // does this work?
    submitFormGC2(state, action) {
      state.submitted = action.payload
      // state.rsvpCode = 'ABC'
      state.rsvpSubmission = {
        rsvpStatus: state.rsvpStatus,
        pair_first_last: action.payload
      }
    },
    clearForm(state) {
      state.rsvpStatus = 'undecided'
      state.firstName = ""
      state.lastName = "" 
      state.pronouns = "" 
      state.phoneNumberCountryCode = ""
      state.phoneNumber = "" 
      state.email = "" 
      state.streetAddress = "" 
      state.secondAddress = ""
      state.city = ""
      state.zipcode = ""  
      state.country = "" 
      state.stateProvince = ""
      state.canContinueDietary = false
      state.drinkAlcohol = true
      state.eatMeat = true
      state.eatDairy = true
      state.eatFish = true
      state.eatShellfish = true
      state.eatEggs = true
      state.eatGluten = true
      state.eatPeanuts = true
      state.moreRestrictions = ""
      state.dateLinkRequested = false
      state.guestCode = ""
    }  
  }
})

export const { rsvpCodeInput, guestCodeInput, rsvpStatusInput, firstNameInput, lastNameInput, pronounsInput, phoneNumberCountryCodeInput,
  phoneNumberInput, emailInput, streetAddressInput, secondAddressInput, cityInput, zipcodeInput, countryInput, stateProvinceInput,
  continueDietary, drinkAlcoholToggle, eatMeatToggle, eatDairyToggle, eatFishToggle, eatShellfishToggle,
  eatEggsToggle, eatGlutenToggle, eatPeanutsToggle, moreRestrictionsInput, dateLinkRequestedInput, clearForm,
  submitFormGC1, submitFormGC1_5, submitFormGC2 } = rsvpSlice.actions

export default rsvpSlice.reducer
