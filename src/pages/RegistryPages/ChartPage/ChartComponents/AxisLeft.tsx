import { useMemo } from "react";
import { ScaleLinear } from "d3"

type AxisLeftProps = {
    yScale: ScaleLinear<number, number>;
    pixelsPerTick: number;
    width: number;
}

const TICK_LENGTH = 5

export const AxisLeft = ({ yScale, pixelsPerTick, width }: AxisLeftProps) => {
    const range = yScale.range();
    
    const ticks = useMemo(() => {
        const height = range[0] - range[1];
        const numberOfTicksTarget = Math.floor(height / pixelsPerTick);
        
        return yScale.ticks(numberOfTicksTarget).map((value) => ({
            value,
            yOffset: yScale(value),
        }))
    }, [yScale]);

    const ticksCenter = useMemo(() => {
        const height = range[1] - range[0];
        const numberOfTicksTarget = 1
    
        return yScale.ticks(numberOfTicksTarget).map((value) => ({
            value,
            yOffset: yScale(value),
        }))
    }, [yScale])

    return (
        <>
            {ticks.map(({ value, yOffset }) => (
                <g 
                    key={value}
                    transform={`translate(0, ${yOffset})`}
                >
                    <line   
                        x1={-TICK_LENGTH}
                        x2={width + TICK_LENGTH}
                        stroke="#33255c"
                        strokeWidth={1}
                        shapeRendering={"crispEdges"}
                        opacity={0.3}
                        strokeDasharray={"3,3"}
                    />
                    <text
                        key={value}
                        style={{
                            fontSize: "10px",
                            textAnchor: "middle",
                            transform: "translateX(-20px)",
                            fill: "#33255c",
                        }}
                    >
                        {value}
                    </text>
                </g>
            ))}
            {ticksCenter.map(({ value, yOffset }) => (
                <>
                    <g 
                        key={value}
                        transform={`translate(0, ${yOffset})`}
                    >
                        <line   
                            x1={-TICK_LENGTH}
                            x2={width + TICK_LENGTH}
                            stroke="#33255c"
                            strokeWidth={1}
                            shapeRendering={"crispEdges"}
                            opacity={0.8}
                        />
                    </g>
                    <text
                        x={-yOffset}
                        y={-35}
                        textRendering={"optimizeLegibility"}
                        dominantBaseline={"Auto"}
                        // transform={"rotate(-90deg)"}
                        style={{
                            fontSize: "12px",
                            textAnchor: "middle",
                            fill: "#33255c",
                            fontWeight: "bold",
                            transform: "rotate(-90deg)"
                        }}
                    >
                        Art Score (Utility to Art)
                    </text>
                </>
            ))}
        </>
    )
}