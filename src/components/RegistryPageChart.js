import { ResponsiveScatterPlot } from "@nivo/scatterplot";
import { useState, useRef, useEffect } from "react";
import { VictoryContainer, VictoryChart, VictoryAxis, VictoryScatter, VictoryTheme, VictoryTooltip, VictoryVoronoiContainer } from "victory";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";

const gift_data_victory = [
    { x: 1,   y: 2,   label: "This gift", id: 1 },
    { x: 2,   y: 3,   label: "Another gift", id: 2 },
    { x: 3,   y: 5,   label: "Something else", id: 3 },
    { x: 4,   y: 4,   label: "Buy me", id: 4 },
    { x: 5,   y: 7,   label: "Sale Sale Sale", id: 5 },
    { x: -10, y: 10,  label: "That gift", id: 6 },
    { x: 10,  y: 10,  label: "Dont forget to resgister", id: 7 },
    { x: -10, y: -10, label: "Present", id: 8 },
    { x: 10,  y: -10, label: "Wedding gift", id: 9 },
]

const gift_data_info = [
    { id: 1, name: "Teapot" },
    { id: 2, name: "Toaster" },
    { id: 3, name: "Towels" },
    { id: 4, name: "Painting" },
    { id: 5, name: "Cups" },
    { id: 6, name: "Forks" },
    { id: 7, name: "Wine" },
    { id: 8, name: "Table" },
    { id: 9, name: "Toy" },
]

const gift_data_d3 = [
    { x: 1,   y: 2,   id: 1 },
    { x: 2,   y: 3,   id: 2 },
    { x: 3,   y: 5,   id: 3 },
    { x: 4,   y: 4,   id: 4 },
    { x: 5,   y: 7,   id: 5 },
    { x: -10, y: 10,  id: 6 },
    { x: 10,  y: 10,  id: 7 },
    { x: -10, y: -10, id: 8 },
    { x: 10,  y: -10, id: 9 },
]

// react example
// using 
        // this site is doing this https://dev.to/julienassouline/let-s-get-started-with-react-and-d3-2nd7

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
    
    const axis = xScale.ticks(10).map((d, i) => (
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
        

export function RegistryChartD3( ) {
        const data = gift_data_victory,
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
            onMouseDown={() => console.log(d)}
        />
        ));

        return (
            <div>
                <svg width={w} height={h}>
                    <g transform={`translate(${margin.left},${margin.top})`}>
                        <AxisLeft yScale={yScale} width={width}>
                        </AxisLeft>
                        <AxisBottom xScale={xScale} height={height} />
                        <AxisLeftZero yScale={yScale} width={width} />
                        <AxisBottomZero xScale={xScale} height={height} />
                        {circles}
                    </g>
                </svg>
            </div>
        )
    }


// export function RegistryChartD3() {
//     const data = useState([
//         [1, 2],
//         [2, 3],  
//         [3, 5], 
//         [4, 4], 
//         [5, 7],
//         [-10, 10],
//         [10, 10],
//         [-10, -10],
//         [10, -10]
//     ])

//     const svgRef = useRef()


//         // setting up the container
//         const w = 500;
//         const h = 300;
//         const svg = d3.select(svgRef.current)
//             .attr('width', w)
//             .attr('height', h)
//             .style('overflow', 'visible')
//             .style('margin', '100px');

//         // setting up the scaling
//         const xScale = d3.scaleLinear()
//             .domain([-10, 10])
//             .range([0, w]);
//         const yScale = d3.scaleLinear()
//             .domain([10, -10])
//             .range([0, h]);

//         // setting up the axis
//         const xAxis = d3.axisBottom(xScale).ticks(10);
//         const yAxis = d3.axisLeft(yScale).ticks(10);
//         svg.append('g')
//             .call(xAxis)
//             .attr('transform', `translate(0, ${h})`);
//         svg.append('g')
//             .call(yAxis);

//         // setting up the axis labeling
//         svg.append('text')
//             .attr('x', w/2)
//             .attr('y', h+50)
//             .text('x');
//         svg.append('text')
//             .attr('y', h/2)
//             .attr('x', -50)
//             .text('y');

//         // setting up svg data
//         svg.selectAll()
//             .data(data)
//             .enter()
//             .append('circles')
//                 .attr('cx', d => xScale(d[0]))
//                 .attr('cy', d => yScale(d[1]))
//                 .attr('r', 4)
//                 .attr('fill', '#78416f');
        


//     return (
//         <div>
//             <svg ref= {svgRef}> 
//                 <g transform={`translate(${100},${100})`}>
//                     {circles}
//                 </g>
//             </svg>
//         </div>
//     )
// }



// export function RegistryChartVictory() { 

//     const [xyz, setXyz] = useState({externalMutations: undefined});
//     const [selectedGift, setSelectedGift] = useState(null);
    
//     function removeMutation() {
//         setXyz({
//           externalMutations: undefined
//         });
//     }

//     function clearClicks() {
//         setXyz({
//           externalMutations: [
//             {
//               childName: "Bar-1",
//               target: ["data"],
//               eventKey: "all",
//               mutation: () => ({ style: undefined }),
//               callback: removeMutation
//             }
//           ]
//         });
//     }

//     function logSelectedGift() {
//         setSelectedGift()
//     }

//     function showSelected() {
//         setSelectedGift()
//     }

//     return(
//         <div style={{ height: "400px", width: "800px" }}>
//             <VictoryChart
//                 containerComponent={<VictoryVoronoiContainer/>}
//                 //theme={VictoryTheme.material}
//                 domain={{ x: [-10, 10], y: [-10, 10] }}
//                 // externalEventMutations={xyz.externalMutations}
//                 // events={[
//                 //     {
//                 //         target: "data",
//                 //         childName: "dot-1",
//                 //         eventHandlers: {
//                 //             onClick: () => ({
//                 //                 target: "data",
//                 //                 mutation: () => ({ style: { fill: "orange" } })
//                 //             })
//                 //         }
//                 //     }
//                 // ]}
//                 >
//                 {/* <VictoryAxis crossAxis
//                     width={400}
//                     height={400}
//                     domain={[-10, 10]}
//                     theme={VictoryTheme.material}
//                     //offsetY={200}
//                     standalone={false}
//                 />
//                 <VictoryAxis dependentAxis crossAxis
//                     width={400}
//                     height={400}
//                     domain={[-10, 10]}
//                     theme={VictoryTheme.material}
//                     //offsetX={200}
//                     standalone={false}
//                 /> */}
//                 <VictoryScatter
//                     name = "dot-1"
//                     size={(datum, active) => active ? 10 : 7}
//                     labelComponent={<VictoryTooltip/>}
//                     style={{ data: { fill: "#c43a31" }, labels: { fill: "#c43a31" } }}
//                  //   size={7}
//                     data={gift_data_victory}
//                     // events={[{
//                     //   target: "data",
//                     //   eventHandlers: {
//                     //     onMouseOver: () => {
//                     //       return [
//                     //         {
//                     //           target: "data",
//                     //           mutation: () => ({style: {fill: "gold", width: 30}})
//                     //         }, {
//                     //           target: "labels",
//                     //           mutation: () => ({ active: true })
//                     //         }
//                     //       ];
//                     //     },
//                     //     onMouseOut: () => {
//                     //       return [
//                     //         {
//                     //           target: "data",
//                     //           mutation: () => {}
//                     //         }, {
//                     //           target: "labels",
//                     //           mutation: () => ({ active: false })
//                     //         }
//                     //       ];
//                     //     }
//                     //   }
//                     // }]}
//                 />
//             </VictoryChart>
//         </div>
//     )
// }

// const gift_data_nivo = 
// [
//     {
//         "id": "bought",
//         "data": [
//             {
//                 "x": -2,
//                 "y": 7,
//                 "z": 1
//             },
//             {
//                 "x": 3,
//                 "y": 1,
//                 "z": 2
//             }
//         ],
//     },
//     {
//         "id": "unbought",
//         "data": [
//             {
//                 "x": -1,
//                 "y": -4,
//                 "z": 3
//             },
//             {
//                 "x": -1.2,
//                 "y": 9,
//                 "z": 4
//             }
//         ],
//     }
// ]

// export function RegistryChartNivo() {
//     return(
//     <div style={{ height: "400px", width: "800px" }}>
//     <ResponsiveScatterPlot
//         data={gift_data_nivo}
//         margin={{ top: 60, right: 140, bottom: 70, left: 90 }}
//         xScale={{ type: 'linear', min: -10, max: 10 }}
//         xFormat=">-.2f"
//         yScale={{ type: 'linear', min: -10, max: 10 }}
//         yFormat=">-.2f"
//         blendMode="multiply"
//         axisTop={null}
//         axisRight={null}
//         axisBottom={{
//             orient: 'bottom',
//             tickSize: 2,
//             tickPadding: 5,
//             tickRotation: 0,
//             legend: 'size',
//             legendPosition: 'middle',
//             legendOffset: 0,
//             truncateTickAt: 0
//         }}
//         axisLeft={{
//             orient: 'left',
//             tickSize: 2,
//             tickPadding: 5,
//             tickRotation: 0,
//             legend: 'function',
//             legendPosition: 'middle',
//             legendOffset: 0,
//             truncateTickAt: 0
//         }}
        
//         legends={[
//             {
//                 anchor: 'bottom-left',
//                 direction: 'row',
//                 justify: false,
//                 translateX: 20,
//                 translateY: 40,
//                 itemWidth: 100,
//                 itemHeight: 12,
//                 itemsSpacing: 5,
//                 itemDirection: 'left-to-right',
//                 symbolSize: 12,
//                 symbolShape: 'circle',
//                 effects: [
//                     {
//                         on: 'hover',
//                         style: {
//                             itemOpacity: 1
//                         }
//                     }
//                 ]
//             }
//         ]}
//     />
//     </div>
//     )
// }

// //export default RegistryChartNivo;
