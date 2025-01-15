import React from 'react';
import { DataBody } from '../components/DataBody';

export function Data() {

  const pageMainColor = "blue" 
  const pageSection = "data"

  return (
    <main className="section-content w-full flex-grow bg-teal-400/75 border-teal-500/50 border-2">
      <DataBody />
    </main> 
  )
};
