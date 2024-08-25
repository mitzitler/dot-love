import React, { useEffect, useRef, useState } from "react";
import { NeatConfig, NeatGradient } from "@firecms/neat";

export const GradientComponent /* :  React.FC */ = (bgColor) => {

    const canvasRef = useRef(HTMLCanvasElement);
    const gradientRef = useRef(NeatGradient);

    useEffect(() => {

        if (!canvasRef.current)
            return;

        gradientRef.current = new NeatGradient({
            ref: canvasRef.current,
            "colors": [
                {
                    "color": "#ab094c",
                    "enabled": true
                },
                {
                    "color": "#ebddcd",
                    "enabled": true
                },
                {
                    "color": "#e8cbc3",
                    "enabled": true
                },
                {
                    "color": "#100847",
                    "enabled": true
                },
                {
                    "color": "#a2d2ff",
                    "enabled": false
                }
            ],
            "speed": 4,
            "horizontalPressure": 3,
            "verticalPressure": 3,
            "waveFrequencyX": 2,
            "waveFrequencyY": 4,
            "waveAmplitude": 5,
            "shadows": 0,
            "highlights": 2,
            "colorSaturation":  3,
            "colorBrightness":  1,
            "wireframe": true,
            "colorBlending": 5,
            "backgroundAlpha": 1,
            "resolution": 1
        });

        return gradientRef.current.destroy;

    }, [canvasRef.current]);

    return (
        <canvas
            className= {bgColor} 
            style={{
                isolation: "isolate",
                height: "100",
                width: "100%",
            }}
            ref={canvasRef}
        />
    );
};