import { useState } from "react";
import { LineChart, Line, ScatterChart, Scatter, CartesianGrid, XAxis, YAxis,  Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { RegistryChartVictory } from "./RegistryPageChart";
import '../App.css';

export function RegistryPage() {

{/*
    return (
    <RegistryChartNivo class="card" style={{width: "500px" }}/>
    )
    */}

    return (
        <div class="m-auto grid grid-cols-3 gap-2">
            <RegistryChartVictory class="card" style={{width: "500px" }}/>
            <div class="card" style={{width: "300px" }}>
                <h1 class="card-title">This is where we see the description for the gift</h1>
                <p class="card-body">More information</p>
            </div>
        </div>
    )
}

const gift_data = [
    {
        "id": 1,
        "gift_name": "x",
        "gift_description": "",
        "gift_link": "",
        "gift_price": 10,
        "x": -2,
        "y": 7,
        "claimed": false
    },
    {
        "id": 2,
        "gift_name": "y",
        "gift_description": "",
        "gift_link": "",
        "gift_price": 20,
        "x": 3,
        "y": 1,
        "claimed": false
    },
    {
        "id": 13,
        "gift_name": "z",
        "gift_description": "",
        "gift_link": "",
        "gift_price": 50,
        "x": -1,
        "y": -4,
        "claimed": false
    },
  ]


// const MyLineChart = () => <Line axisLeft={{ renderTick: (value) => <text style={{ fontWeight: value === 0 ? 'bold' : 'normal'}}>{value}</text> }} />

// export function RegistryPageRechart({gift_data}){
//     //static demoUrl = 'https://codesandbox.io/p/sandbox/scatter-chart-of-three-dimensions-nqkj42';
  
//       return (
//         <ResponsiveContainer width="100%" height={400}>
//           <ScatterChart
//             margin={{
//               top: 20,
//               right: 20,
//               bottom: 20,
//               left: 20,
//             }}
//           >
//             <CartesianGrid />
//             <XAxis type="number" dataKey="x" name="Size Score"/>
//             <YAxis type="number" dataKey="y" name="Artsy Score "/>
//             <Tooltip cursor={{ strokeDasharray: '3 3' }} />
//             <Legend />
//             {/* 
//             The two data sets will be if claimed is true or false
//             <Scatter name="Available" data={gift_data} fill="#100847" shape="circle" />
//             <Scatter name="Not available" data={gift_data} fill="#100847" shape="circle" /> 
//             */}
//             <Scatter name="Available" data={gift_data} fill="#100847" shape="circle" />
//           </ScatterChart>
//         </ResponsiveContainer>
//       );
// }
