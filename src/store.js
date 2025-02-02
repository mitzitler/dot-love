import { configureStore, combineReducers } from '@reduxjs/toolkit'
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import rsvpReducer from "./features/guest/rsvpSlice";
import rsvpCompletedReducer from "./features/guest/rsvpCompletedSlice";
import userReducer from "./features/guest/userSlice";
import { gizmoApi } from './services/gizmo';

const persistConfig = {
    key: 'root',
    storage, // storage mechanism
    whitelist: ['rsvp', 'rsvpCompleted', 'user'], // this is the list of reducers to persist
}

const rootReducer = combineReducers({
    rsvp: rsvpReducer,
    rsvpCompleted: rsvpCompletedReducer,
    user: userReducer,
    [gizmoApi.reducerPath]: gizmoApi.reducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer)

const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
            },
        }).concat(gizmoApi.middleware)
})

const persistor = persistStore(store)

export { store, persistor }
