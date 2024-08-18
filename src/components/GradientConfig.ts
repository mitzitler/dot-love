

import { NeatConfig, NeatGradient } from "@firecms/neat";

export const config: NeatConfig = {
/* preset: pastel */

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
    "colorBrightness": 1,
    "colorSaturation": 3,
    "wireframe": false,
    "colorBlending": 5,
    "backgroundColor": "#003FFF",
    "backgroundAlpha": 1,
    "resolution": 1

    /* mitzi custom */
/*
    colors: [
      {
        color: "#E8CBC3",
        enabled: true,
      },
      {
        color: "#E4B9B9",
        enabled: true,
      },
      {
        color: "#EBDDCD",
        enabled: true,
      },
      {
        color: "#DF7A97",
        enabled: true,
      },
      {
        color: "#c81d25",
        enabled: false,
      },
    ],
    speed: 2,
    horizontalPressure: 5,
    verticalPressure: 7,
    waveFrequencyX: 5,
    waveFrequencyY: 3,
    waveAmplitude: 7,
    shadows: 2,
    highlights: 7,
    colorBrightness: 1,
    colorSaturation: 8,
    wireframe: true,
    colorBlending: 4,
    backgroundColor: "#FF0000",
    backgroundAlpha: 1,
    resolution: 1.6,


    */
  };



// define an element with id="gradient" in your html
const neat = new NeatGradient({
  ref: <HTMLCanvasElement> document.getElementById("gradient")!,
  ...config
});

// you can change the config at any time
neat.speed = 6;

// you can also destroy the gradient for cleanup
// e.g. returning from a useEffect hook in React
neat.destroy();