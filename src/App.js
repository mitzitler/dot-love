import React from 'react';
import Router from './routes/Router';
import { GenericHeader } from './components/GenericHeader';

export default function App() {
  return (
    <div className="w-full min-h-screen flex flex-col overflow-hidden">
      <GenericHeader />
      <Router />
      {/* <GenericFooter if i want this /> */}
    </div>
  );
}

