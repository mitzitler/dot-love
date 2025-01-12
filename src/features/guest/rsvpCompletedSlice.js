import { createSlice } from '@reduxjs/toolkit'

const rsvpCompletedSlice = createSlice({
  name: "rsvpCompleted",
  initialState: {
    submitted: null,
    rsvpSubmission: "",
  },
  reducers: {
    storeCompletedRSVP(state, action) {
      state.submitted = action.payload[0] // this is the first_last
      state.rsvpSubmission = action.payload[1] // this is the complete element
    },
  }
})

export const { storeCompletedRSVP } = rsvpCompletedSlice.actions
  
export default rsvpCompletedSlice.reducer