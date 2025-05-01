import { createSlice } from '@reduxjs/toolkit'

const extrasSlice = createSlice({
  name: "extras",
  initialState: {
    loginHeaderState: '',
    giftClaimed: {}, // id: , claimed: boolean, 
  },
  reducers: {
    giftClaimedToggle(state, action) {
      // id = action.payload[0]
      // claimed = action.payload[1]
      // toggle the claimed state to opposite
      state.giftClaimed[action.payload[0]] = !action.payload[1] 
      console.log('for item id', action.payload[0], 'the claimed state is now', action.payload[1])
    },
    setloginHeaderState(state, action) {
      state.loginSuccessState = action.payload
      console.log('The login header for this session is: ', action.payload)
    }
  }
})

export const { giftClaimedToggle, setloginHeaderState } = extrasSlice.actions
  
export default extrasSlice.reducer