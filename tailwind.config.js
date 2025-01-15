// /** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ...colors,
        cyan: colors.cyan,
        babyblue: {
          400: '#BAE8EA',
          500: '#87D6D9'
        },
        lilac: {
          400: '#CDC8FA',
          500: '#C3BEED'
        }
      }
    },
  },
}


