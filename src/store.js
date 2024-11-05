import { configureStore } from '@reduxjs/toolkit'
import nameReducer from "./features/guest/nameSlice";

const store = configureStore({
    reducer: {
        name: nameReducer
    }
})

export default store