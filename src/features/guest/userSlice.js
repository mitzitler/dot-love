import { createSlice } from '@reduxjs/toolkit'

const userSlice = createSlice({
  name: "user",
  initialState: {
    fullNameCode: '',
  },
  reducers: {
    fullNameCodeInput(state, action) {
      state.fullNameCode = action.payload
    },
  }
})

export const { fullNameCodeInput } = userSlice.actions
  
export default userSlice.reducer