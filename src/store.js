import { configureStore } from '@reduxjs/toolkit'
import rsvpReducer from "./features/guest/rsvpSlice";
import { gizmoApi } from './services/gizmo';

const store = configureStore({
    reducer: {
        rsvp: rsvpReducer,
        [gizmoApi.reducerPath]: gizmoApi.reducer,

    }
})

export default store
