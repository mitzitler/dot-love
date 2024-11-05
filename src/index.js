import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { BrowserRouter } from "react-router-dom";
import store from './store'

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

console.log('Initial state: ', store.getState())

const unsubscribe = store.subscribe(() =>
  console.log('State after dispatch: ', store.getState())
)

store.dispatch({ type: 'name/nameRsvped', payload: 'ATTENDING' })