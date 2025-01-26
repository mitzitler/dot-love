import { createSlice } from '@reduxjs/toolkit'

const rsvpCompletedSlice = createSlice({
  name: "rsvpCompleted",
  initialState: {
    submitted: null,
    completedRsvps: [],
  },
  reducers: {
    storeCompletedRSVP(state, action) {
      state.submitted = action.payload.submissionKey
      state.completedRsvps.push({
        guestInfo: action.payload.fullGuestInfo
      });
    },
    clearCompleteRSVPs(state) {
      state.completedRsvps = [];
    }
  }
})

export const { storeCompletedRSVP, clearCompleteRSVPs } = rsvpCompletedSlice.actions
  
export default rsvpCompletedSlice.reducer
