import { useState, useRef, useEffect } from "react";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";
import 'react-tippy/dist/tippy.css'
import { AxisBottom } from "./ChartComponents/AxisBottom";
import { AxisLeft } from "./ChartComponents/AxisLeft";
import { Tooltip, InteractionData } from "./ChartComponents/Tooltip";
import '../styles/Registry.css'
import { AxisTop } from "./ChartComponents/AxisTop";

// doing this: https://www.react-graph-gallery.com/scatter-plot

type DataPoint = {
    item_id: number;
    size_score: number;
    function_score: number;
    price_cents: number;
    has_dollar_value: boolean;
    price_cat: string;
    name: string;
    brand: string;
    descr: string;
    claim_state: boolean;
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

    const [chartWidth, setChartWidth] = useState(width)
    const [chartHeight, setChartHeight] = useState(height)

    useEffect(() => {
      const handleResize = () => {
        if (window.innerWidth <= 450) {
          // im not picky, it could also be 
          console.log('the window innerwidth is less than or equal to 450')
          // setChartWidth(window.innerWidth - margins[1] - margins[3]);
          // setChartHeight(window.innerWidth - margins[1] - margins[3])
          setChartWidth(340)
          setChartHeight(340)
          console.log('new width', chartWidth)
          console.log('new height', chartHeight)
        } else {
          setChartWidth(width)
          setChartHeight(height)
        }
      }

      window.addEventListener("resize", handleResize)

      // this is an initial check ?
      handleResize()

      return () => window.removeEventListener("resize", handleResize)

    }, [width, height, margins])

    const boundsWidth = chartWidth - margins[1] - margins[3]
    const boundsHeight = chartHeight - margins[0] - margins[2]

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
            r={!d.claim_state ? 8 : 5}
            cx={xScale(d.size_score)}
            cy={yScale(d.function_score)}
            stroke={colorScale(d.price_cat)}
            fill={colorScale(d.price_cat)}
            fillOpacity={0.7}
            onMouseEnter={() =>
              setHovered({
                xPos: xScale(d.size_score),
                yPos: yScale(d.function_score),
                name: d.name,
                price: d.price_cents/100
              })
            }
            onMouseLeave={() => setHovered(null)}
            onClick={() => setDisplayedId(d.item_id)}
          />
        );
      });

    //   console.log("colorScale: ", colorScale)
    //   console.log("allShapes: ", allShapes)

      return (
        <div className="text-center">
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
                {/* <Tooltip interactionData={hovered} /> */}
            </div>
        </div>
      );
}