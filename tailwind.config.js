// /** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  safelist: [
    'bg-amber-400/75',
    'border-amber-500/50',
    'bg-babyblue-400/75',
    'border-babyblue-500/50',
    'bg-lilac-400/75',
    'border-lilac-500/50',
    'bg-raspberry-400/75',
    'border-raspberry-500/50',
    'bg-lime-400/75',
    'border-lime-500/50',
    'bg-emerald-400/75',
    'border-emerald-500/50',
    'bg-lime-400/75',
    'border-lime-500/50',
    'bg-fuchsia-400/75',
    'border-fuchsia-500/50',
    'bg-khaki-400/75',
    'border-khaki-500/50',

  ],
  theme: {
    extend: {
      colors: {
        ...colors,
        cyan: colors.cyan,
        lime: colors.lime,
        babyblue: {
          400: '#BAE8EA',
          500: '#87D6D9'
        },
        lilac: {
          400: '#CDC8FA',
          500: '#C3BEED'
        },
        raspberry: {
          400: '#db5186',
          500: '#ed2872'
        },
        khaki: {
          400: '#d9d0b2',
          500: '#b5a982'
        },
        terracotta: {
          400: "#DE6B54",
          500: "#DE6B54"
        },
        plum: {
          400: "#902E6B",
          500: "#902E6B"
        },
        cream: {
          400: "#FBFBF2",
          500: "#FBFBF2"
        }
      }
    },
  },
}


