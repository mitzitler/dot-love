import { useState, useRef } from "react";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";

// figure out useSpring from "react-spring"

const gift_data = [
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


function AxisLeft({ yScale, width }) {
    const textPadding = -20
    
        const axis = yScale.ticks(10).map((d, i) => (
        <g key={i} className="y-tick">
            <line
            style={{ stroke: "#e4e5eb" }}
            y1={yScale(d)}
            y2={yScale(d)}
            x1={0}
            x2={width}
            />
            <text
            style={{ fontSize: 12, fill: "#782614" }}
            x={textPadding}
            dy=".32em"
            y={yScale(d)}
            >
            {d}
            </text>
        </g>
        ));
    return <>{axis}</>;
};

function AxisLeftZero({ yScale, width}) {
    const axis = yScale.ticks(10).map((d, i) => (
        <g key={i} className="y-tick-zero">
            <line
            style={{ stroke: d != 0 ? "#e4e5eb" : "#782614", strokeWidth: d != 0 ? "0px" : "2px" }}
            y1={yScale(d)}
            y2={yScale(d)}
            x1={0}
            x2={width}
            />
        </g>
        ));
    return <>{axis}</>;
}
        
function AxisBottom({ xScale, height }) {
    const textPadding = 10;
    const range = xScale.range()
    const axis = xScale.ticks(10).map((d, i) => (
        <>
        <g className="x-tick" key={i}>
        <line
            style= {{ stroke: "#e4e5eb" }}
            y1={0}
            y2={height}
            x1={xScale(d)}
            x2={xScale(d)}
        />
        <text
            style={{ textAnchor: "middle", fontSize: 12, fill: "#782614" }}
            dy=".71em"
            x={xScale(d)}
            y={height + textPadding}
        >
            {d}
        </text>
        </g>
        </>
    ));
    return <>{axis}</>;
};

function AxisBottomZero({ xScale, height }) {    
    const axis = xScale.ticks(10).map((d, i) => (
        <g className="x-tick-zero" key={i}>
        <line
            style= {{ stroke: d != 0 ? "#e4e5eb" : "#782614", strokeWidth: d != 0 ? "0px" : "2px"}}
            y1={0}
            y2={height}
            x1={xScale(d)}
            x2={xScale(d)}
        />
        </g>
    ));
    return <>{axis}</>;
};
        

export function RegistryChartD3() {
    const [activeGift, setActiveGift] = useState(null)
    const chartRef = useRef();
    const tooltipRef = useRef(null);

    function handleActiveGift(giftInput) {
    //    giftRef.current.focus()
        setActiveGift(giftInput)
       console.log("function says active gift id is " + giftInput)
    }

    console.log("component says active gift id is " + activeGift)

    const data = gift_data,
        w = 500,
        h = 500,
        margin = {
            top: 60,
            bottom: 60,
            left: 60,
            right: 60
        };

    const width = w - margin.right - margin.left,
        height = h - margin.top - margin.bottom;

    const xScale = scaleLinear()
        .domain([-10, 10])
        .range([0, width]);

    const yScale = scaleLinear()
        .domain([-10, 10])
        .range([height, 0]);

    const circles = data.map((d, i) => (
        <circle
            key={i}
            r={6}
            cx={xScale(d.x)}
            cy={yScale(d.y)}
            opacity={1}
            stroke="#78416f"
            fill="#78416f"
            fillOpacity={0.2}
        //    ref={giftRef}
            value={d.id}
            onClick={() => handleActiveGift(d.id)}
        />
    ));

    return (
        <div>
            <svg ref={chartRef} width={w} height={h}>
                <g transform={`translate(${margin.left},${margin.top})`}>
                    <AxisLeft yScale={yScale} width={width}>
                    </AxisLeft>
                    <AxisBottom xScale={xScale} height={height} />
                    <AxisLeftZero yScale={yScale} width={width} />
                    <AxisBottomZero xScale={xScale} height={height} />
                    <text
                        textAnchor = "middle"
                        transform = "rotate(-90)"
                        x = {-height / 2} 
                        y ={-(margin.left * 0.75)}
                    //    fontWeight = {text = 'Art Score' ? "bold" : ""}
                        >
                        Art score: most practical to most artsy 
                    </text>
                    <text
                        textAnchor = "middle"
                        x = {width / 2} 
                        y ={height + (margin.bottom * 0.75)} 
                        markdown = "1"> 
                        Size score: smallest to largest
                    </text>
                    {circles}
                </g>
            </svg>
        </div>
    )
}