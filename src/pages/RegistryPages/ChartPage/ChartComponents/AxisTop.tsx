import { useMemo } from "react";
import { ScaleLinear } from "d3";

type AxisTopProps = {
    xScale: ScaleLinear<number, number>;
    pixelsPerTick: number;
    height: number;
    PRICE_CAT_DICT: Record<string, string>;
}

const TICK_LENGTH = 10

export const AxisTop = ({ xScale, pixelsPerTick, height, PRICE_CAT_DICT }: AxisTopProps) => {

    const ticksLegend = useMemo(() => {
        const PRICE_CAT_ARRAY = Object.keys(PRICE_CAT_DICT);
        const step = xScale.range()[1] / PRICE_CAT_ARRAY.length;
    
        return PRICE_CAT_ARRAY.map((category, index) => ({
            value: index,
            xOffset: step * index + step / 2, // center circles
            category,
            color: PRICE_CAT_DICT[category] || "Unknown",
        }));
    }, [xScale, PRICE_CAT_DICT]);

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