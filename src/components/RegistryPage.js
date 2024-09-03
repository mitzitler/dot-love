import { useState } from "react";
import { LineChart, Line, ScatterChart, Scatter, CartesianGrid, XAxis, YAxis,  Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { RegistryChartD3 } from "./RegistryPageChart";
import '../App.css';

const Data = [
    { x: 1,   y: 2,   id: 1, name: "Teapot"  },
    { x: 2,   y: 3,   id: 2, name: "Toaster" },
    { x: 3,   y: 5,   id: 3, name: "Towels" },
    { x: 4,   y: 4,   id: 4, name: "Painting" },
    { x: 5,   y: 7,   id: 5, name: "Cups" },
    { x: -10, y: 10,  id: 6, name: "Forks" },
    { x: 10,  y: 10,  id: 7, name: "Wine" },
    { x: -10, y: -10, id: 8, name: "Table" },
    { x: 10,  y: -10, id: 9, name: "Toy" },
]

function RegistryPageChartContainer() {
    // const [chartGift, setChartGift] = useState()

    // function handleChartGiftChange(chartGift) {
    //     setChartGift(chartGift)
    //     console.log("i am the chart gift" + chartGift)
    // }

    // constructor(props) {
    //     super(props);
    //     this.ChildElement = React.createRef()
    // }


    return (
        <div class=" relative m-auto grid grid-cols-3 gap-2 border-4">
            <div class="card col-span-2 width-500 border-2 static" style = {{position: "static"}}>
                <RegistryChartD3 Data={Data}
             //   ref={this.ChildElement} 
                />
            </div>
            <div class="card col-span-1 width-200 border-2 static">
                <h1 class="card-title border-2">This is where we see the description for the gift</h1>
                <p class="card-body border-2">
                    More information, gift id is {}
                </p>
            </div>
        </div>
    )
}





export function RegistryPage() {
    return ( <RegistryPageChartContainer/> )
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
