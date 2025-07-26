/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./ranieri_project/**/*.html",
    './node_modules/preline/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        'roxo1': '#61152d',
        'roxo2': '#681630',
        'laranja1': '#c89c20',
        'laranja2': '#cd862a',
        'laranja3': '#c9583e',
        'preto1': '#0f0e0f',
        'prata1': '#d1d1d1',
        'branco1': '#f8f8f8',
        'verde1': '#2e5935',
        'azul1': '#1b365d',
        'amarelo1': '#c5a100',
        'vermelho1': '#9e1b1b',
        'rosa1': '#a54161',
        'dourado1': '#bfa14f',
        'cinza1': '#8a8a8a',
        'roxo1-hover': '#7a1939',
        'roxo2-hover': '#7a1939',
        'roxo2-focus': '#9c2049',
        'laranja1-hover': '#e0b223',
        'laranja2-hover': '#e6a032',
        'laranja1-focus': '#f3c734',
      },
    },
  },
  plugins: [
    require('preline/plugin'),
  ],
}
