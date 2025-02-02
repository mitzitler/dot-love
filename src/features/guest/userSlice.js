import { createSlice } from '@reduxjs/toolkit'

const userSlice = createSlice({
  name: "user",
  initialState: {
    fullNameCode: '',
    loginSuccess: false
  },
  reducers: {
    fullNameCodeInput(state, action) {
      state.fullNameCode = action.payload
    },
    loginSuccessInput(state, action) {
      state.loginSuccess = action.payload
    }
  }
})

export const { fullNameCodeInput, loginSuccessInput } = userSlice.actions
  
export default userSlice.reducer