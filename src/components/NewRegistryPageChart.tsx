import { useState, useRef, useEffect } from "react";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";
import 'react-tippy/dist/tippy.css'
import { AxisBottom } from "./chart/AxisBottom";
import { AxisLeft } from "./chart/AxisLeft";
import { Tooltip, InteractionData } from "./chart/Tooltip";
import '../styles/Registry.css'
import { AxisTop } from "./chart/AxisTop";

// doing this: https://www.react-graph-gallery.com/scatter-plot

type DataPoint = {
    id: number;
    x: number;
    y: number;
    price: number;
    price_cat: string;
    name: string;
    description: string;
  };
  
  type ScatterplotProps = {
    width: number;
    height: number;
    margins: Array<number>;
    data: DataPoint[];
    displayedId: number;
    setDisplayedId: React.Dispatch<React.SetStateAction<number>>
  };

export const NewRegistryPageChart = ({ width, height, margins, data, displayedId, setDisplayedId }: ScatterplotProps) => {

    const boundsWidth = width - margins[1] - margins[3]
    const boundsHeight = height - margins[0] - margins[2]

    const [hovered, setHovered] = useState<InteractionData | null>(null)
    // const [displayedID, setDisplayedId] = useState<Number | null>()
    // scales
    const yScale = d3.scaleLinear().domain([-10,10]).range([boundsHeight, 0])
    const xScale = d3.scaleLinear().domain([-10,10]).range([0, boundsWidth])
    const allGroups = data.map((d) => String(d.price_cat))
    const colorScale = d3
    .scaleOrdinal<string>()
    .domain(allGroups)
    .range(["#32a852", "#e052eb", "#5eb4ff", "#8037b8", "#e35954"]);

    // this has the two axes being generated in other files too

    const allShapes = data.map((d, i) => {
        return (
          <circle
            key={i}
            r={8}
            cx={xScale(d.x)}
            cy={yScale(d.y)}
            stroke={colorScale(d.price_cat)}
            fill={colorScale(d.price_cat)}
            fillOpacity={0.7}
            onMouseEnter={() =>
              setHovered({
                xPos: xScale(d.x),
                yPos: yScale(d.y),
                name: d.name,
                price: d.price
              })
            }
            onMouseLeave={() => setHovered(null)}
            onClick={() => setDisplayedId(d.id)}
          />
        );
      });

    //   console.log("colorScale: ", colorScale)
    //   console.log("allShapes: ", allShapes)

      return (
        <div className="text-center">
            {/* axis top with the color legend */}
            {/* <span>span</span> */}
            <svg width={width} height={height} display={"block"}>
                <g
                    width={boundsWidth}
                    height={boundsHeight}
                    transform={`translate(${[margins[3], margins[0]].join(",")})`}
                >
                    {/* Top legend */}
                    <g transform={`translate(0, -${boundsHeight})`}>
                        <AxisTop
                        xScale={xScale}
                        pixelsPerTick={40}
                        height={boundsHeight}
                        />
                    </g>

                    {/* Y axis */}
                    <AxisLeft yScale={yScale} pixelsPerTick={40} width={boundsWidth} 
                    />
    
                    {/* X axis, use an additional translation to appear at the bottom */}
                    <g transform={`translate(0, ${boundsHeight})`}>
                        <AxisBottom
                        xScale={xScale}
                        pixelsPerTick={40}
                        height={boundsHeight}
                        />
                    </g>
        
                    {/* Circles */}
                    {allShapes}
                </g>
            </svg>
    
            {/* Tooltip */}
            <div
                style={{
                width: boundsWidth,
                height: boundsHeight,
                position: "absolute",
                top: 0,
                left: 0,
                pointerEvents: "none",
                marginLeft: margins[1],
                marginTop: margins[0],
                }}
            >
                <Tooltip interactionData={hovered} />
            </div>
        </div>
      );
}