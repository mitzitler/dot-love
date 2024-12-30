import { configureStore } from '@reduxjs/toolkit'
import nameReducer from "./features/guest/nameSlice";
import { gizmoApi } from './services/gizmo';

const store = configureStore({
    reducer: {
        name: nameReducer,
        [gizmoApi.reducerPath]: gizmoApi.reducer,
    }
})

export default store
