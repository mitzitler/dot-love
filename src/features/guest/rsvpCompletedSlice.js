import { createSlice } from '@reduxjs/toolkit'

const rsvpCompletedSlice = createSlice({
  name: "rsvpCompleted",
  initialState: {
    submitted: false,
    completedRsvps: [],
  },
  reducers: {
    storeCompletedRSVP(state, action) {
      state.submitted = true;
      state.completedRsvps.push(action.payload.fullGuestInfo);
    },
    clearCompleteRSVPs(state) {
      state.submitted = false;
      state.completedRsvps = [];
    }
  }
})

export const { storeCompletedRSVP, clearCompleteRSVPs } = rsvpCompletedSlice.actions
  
export default rsvpCompletedSlice.reducer
