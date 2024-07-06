import { NeatConfig, NeatGradient } from "@firecms/neat";

export const /*config: NeatConfig */ x = {
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
  };

const neat = new NeatGradient({
  ref: document.getElementById("gradient"),
  ...config,
});
