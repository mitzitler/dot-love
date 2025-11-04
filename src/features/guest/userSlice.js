import { createSlice } from '@reduxjs/toolkit'

const userSlice = createSlice({
  name: "user",
  initialState: {
    fullNameCode: '',
    loginSuccess: false,
    rehearsalDinnerInvited: false,
    guestType: null
  },
  reducers: {
    fullNameCodeInput(state, action) {
      state.fullNameCode = action.payload
    },
    loginSuccessInput(state, action) {
      state.loginSuccess = action.payload
    },
    rehearsalDinnerInvitedInput(state, action) {
      state.rehearsalDinnerInvited = action.payload
    },
    guestTypeInput(state, action) {
      state.guestType = action.payload
    }
  }
})

export const { fullNameCodeInput, loginSuccessInput, rehearsalDinnerInvitedInput, guestTypeInput } = userSlice.actions
  
export default userSlice.reducer