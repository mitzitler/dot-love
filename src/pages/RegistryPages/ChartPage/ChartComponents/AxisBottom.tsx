import { useMemo } from "react";
import { ScaleLinear } from "d3";

type AxisBottomProps = {
    xScale: ScaleLinear<number, number>;
    pixelsPerTick: number;
    height: number
}

const TICK_LENGTH = 5

export const AxisBottom = ({ xScale, pixelsPerTick, height }: AxisBottomProps) => {

    const range = xScale.range()

    const ticks = useMemo(() => {
        const width = range[1] - range[0];
        const numberOfTicksTarget = Math.floor(width / pixelsPerTick)
    
        return xScale.ticks(numberOfTicksTarget).map((value) => ({
            value,
            xOffset: xScale(value),
        }))
    }, [xScale])

    const ticksCenter = useMemo(() => {
        const width = range[1] - range[0];
        const numberOfTicksTarget = 1
    
        return xScale.ticks(numberOfTicksTarget).map((value) => ({
            value,
            xOffset: xScale(value),
        }))
    }, [xScale])

    // console.log("ticks: ", ticks)
    // console.log("range: ", range)

    return (
        <>
            {ticks.map(({value, xOffset}) => (
                <g 
                    key={value} 
                    transform={`translate(${xOffset}, 0)`}
                    shapeRendering={"crispEdges"}
                >
                    <line
                        y1={TICK_LENGTH}
                        y2={-height - TICK_LENGTH}
                        stroke = "#33255c"
                        strokeWidth={1}
                        opacity={0.3}
                        strokeDasharray={"3,3"}
                    />
                    <text
                        key={value}
                        style={{
                          fontSize: "10px",
                          textAnchor: "middle",
                          transform: "translateY(20px)",
                          fill: "#33255c",
                        }}
                      >
                        {value}
                    </text>
                </g>
            ))}
            {ticksCenter.map(({value, xOffset}) => (
                <>
                    <g 
                        key={value} 
                        transform={`translate(${xOffset}, 0)`}
                        shapeRendering={"crispEdges"}
                    >
                        <line
                            y1={TICK_LENGTH}
                            y2={-height - TICK_LENGTH}
                            stroke = "#33255c"
                            strokeWidth={1}
                            opacity={0.8}
                        />
                    </g>
                    <text
                        x={xOffset}
                        y={40}
                        textRendering={"optimizeLegibility"}
                        dominantBaseline={"Auto"}
                        style={{
                            fontSize: "12px",
                            textAnchor: "middle",
                            fill: "#33255c",
                            fontWeight: "bold"
                        }}
                    >
                        Size Score (Small to Large)
                    </text>
                </>
            ))}
        </>
    )
}