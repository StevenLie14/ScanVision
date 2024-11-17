/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './html/*.html',
    './static/js/**/*.js', 
  ],
  theme: {
    extend: {
      colors: {
        'docvision': '#9333EA',
      }
    },
  },
  plugins: [],
}

