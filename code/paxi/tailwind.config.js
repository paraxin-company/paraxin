/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "templates/*.html",
    "templates/**/*.html"
],
  theme: {
    extend: {
      borderWidth: {
        '3': '3px',
      },
      fontFamily:{
        tit:['tit', 'cursive'],
      },
      container: {
        center: true,
        padding: '2rem',
      },
      colors: {
        'paraxin-c': {
          200: '#B2299F',
          300: '#77005d',
        },
        gray: {
          150: '#efefef',
        }
      },
    },
  },
  plugins: [],
}