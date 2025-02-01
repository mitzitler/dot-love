import { createSlice } from '@reduxjs/toolkit'

const rsvpCompletedSlice = createSlice({
  name: "rsvpCompleted",
  initialState: {
    submitted: false,
    completedRsvps: [],
  },
  reducers: {
    storeCompletedRSVP(state, action) {
      state.completedRsvps.push(action.payload);
    },
    clearCompleteRSVPs(state) {
      state.submitted = false;
      state.completedRsvps = [];
    },
    setSubmitted: (state, action) => {
      state.submitted = action.payload;
    }
  }
})

export const { storeCompletedRSVP, clearCompleteRSVPs, setSubmitted } = rsvpCompletedSlice.actions
  
export default rsvpCompletedSlice.reducer
