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
                    "color": "#cdb4db",
                    "enabled": true
                },
                {
                    "color": "#ffc8dd",
                    "enabled": true
                },
                {
                    "color": "#ffafcc",
                    "enabled": true
                },
                {
                    "color": "#bde0fe",
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
            "wireframe": false,
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