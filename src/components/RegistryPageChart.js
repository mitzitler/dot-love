import { ResponsiveScatterPlot } from "@nivo/scatterplot";
import { useState } from "react";
import { VictoryContainer, VictoryChart, VictoryAxis, VictoryScatter, VictoryTheme, VictoryTooltip, VictoryVoronoiContainer } from "victory"

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

export function RegistryChartVictory() { 

    const [xyz, setXyz] = useState({externalMutations: undefined});
    const [selectedGift, setSelectedGift] = useState(null);
    
    function removeMutation() {
        setXyz({
          externalMutations: undefined
        });
    }

    function clearClicks() {
        setXyz({
          externalMutations: [
            {
              childName: "Bar-1",
              target: ["data"],
              eventKey: "all",
              mutation: () => ({ style: undefined }),
              callback: removeMutation
            }
          ]
        });
    }

    function logSelectedGift() {
        setSelectedGift()
    }

    function showSelected() {
        setSelectedGift()
    }

    return(
        <div style={{ height: "400px", width: "800px" }}>
            <VictoryChart
                containerComponent={<VictoryVoronoiContainer/>}
                //theme={VictoryTheme.material}
                domain={{ x: [-10, 10], y: [-10, 10] }}
                // externalEventMutations={xyz.externalMutations}
                // events={[
                //     {
                //         target: "data",
                //         childName: "dot-1",
                //         eventHandlers: {
                //             onClick: () => ({
                //                 target: "data",
                //                 mutation: () => ({ style: { fill: "orange" } })
                //             })
                //         }
                //     }
                // ]}
                >
                {/* <VictoryAxis crossAxis
                    width={400}
                    height={400}
                    domain={[-10, 10]}
                    theme={VictoryTheme.material}
                    //offsetY={200}
                    standalone={false}
                />
                <VictoryAxis dependentAxis crossAxis
                    width={400}
                    height={400}
                    domain={[-10, 10]}
                    theme={VictoryTheme.material}
                    //offsetX={200}
                    standalone={false}
                /> */}
                <VictoryScatter
                    name = "dot-1"
                    size={(datum, active) => active ? 10 : 7}
                    labelComponent={<VictoryTooltip/>}
                    style={{ data: { fill: "#c43a31" }, labels: { fill: "#c43a31" } }}
                 //   size={7}
                    data={gift_data_victory}
                    // events={[{
                    //   target: "data",
                    //   eventHandlers: {
                    //     onMouseOver: () => {
                    //       return [
                    //         {
                    //           target: "data",
                    //           mutation: () => ({style: {fill: "gold", width: 30}})
                    //         }, {
                    //           target: "labels",
                    //           mutation: () => ({ active: true })
                    //         }
                    //       ];
                    //     },
                    //     onMouseOut: () => {
                    //       return [
                    //         {
                    //           target: "data",
                    //           mutation: () => {}
                    //         }, {
                    //           target: "labels",
                    //           mutation: () => ({ active: false })
                    //         }
                    //       ];
                    //     }
                    //   }
                    // }]}
                />
            </VictoryChart>
        </div>
    )
}

const gift_data_nivo = 
[
    {
        "id": "bought",
        "data": [
            {
                "x": -2,
                "y": 7,
                "z": 1
            },
            {
                "x": 3,
                "y": 1,
                "z": 2
            }
        ],
    },
    {
        "id": "unbought",
        "data": [
            {
                "x": -1,
                "y": -4,
                "z": 3
            },
            {
                "x": -1.2,
                "y": 9,
                "z": 4
            }
        ],
    }
]

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
