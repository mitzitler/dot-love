import { useMemo } from "react";
import { ScaleLinear } from "d3";

type AxisTopProps = {
    xScale: ScaleLinear<number, number>;
    pixelsPerTick: number;
    height: number
}

const TICK_LENGTH = 10

export const AxisTop = ({ xScale, pixelsPerTick, height }: AxisTopProps) => {

    const ticksLegend = useMemo(() => {
        const numberOfTicksTarget = 5
        const PRICE_CAT_DICT: Record<string, string> = {
            '0-50' : "#32a852",
            '50-100' : "#e052eb",
            '100-150' : "#5eb4ff",
            '150+' : "#8037b8",
            '??' : "#e35954"
        }

        const PRICE_CAT_ARRAY = Object.keys(PRICE_CAT_DICT);
    
        return xScale.ticks(numberOfTicksTarget).map((value, index) => {
            const category = PRICE_CAT_ARRAY[index] || "Unknown";
            return { 
                value,
                xOffset: xScale(value),
                category,
                color: PRICE_CAT_DICT[category] || "Unknown"
            }
        })
    }, [xScale])

    return (
        <>
            {ticksLegend.map(({value, xOffset, category, color }) => (
                <g 
                    key={category} 
                    shapeRendering={"crispEdges"}
                >
                    <circle
                        key={category}
                        r={5}
                        cx={xOffset}
                        cy={height - TICK_LENGTH - 25}
                        stroke={color}
                        fill={color}
                        fillOpacity={0.8}
                    />
                    <text
                        x={xOffset}
                        y={height - TICK_LENGTH - 5}
                        textRendering={"optimizeLegibility"}
                        dominantBaseline={"Auto"}
                        style={{
                            fontSize: "9px",
                            textAnchor: "middle",
                            fill: "#33255c",
                        }}
                    >
                        {category}
                    </text>
                </g>
            ))}
        </>
    )
}