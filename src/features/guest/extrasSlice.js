import { createSlice } from '@reduxjs/toolkit'

const extrasSlice = createSlice({
  name: "extras",
  initialState: {
    loginHeaderFirstLast: {},
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
    setloginHeaderFirstLast(state, action) {
      state.loginHeaderFirstLast = Object.values(action.payload)
    },
    setloginHeaderState(state, action) {
      state.loginHeaderState = Object.values(action.payload)[0]
      console.log('The login header for this session is: ', Object.values(action.payload)[0])
    }
  }
})

export const { giftClaimedToggle, setloginHeaderFirstLast, setloginHeaderState } = extrasSlice.actions
  
export default extrasSlice.reducer