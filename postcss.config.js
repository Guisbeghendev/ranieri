// postcss.config.js
// Este arquivo configura o PostCSS para usar os plugins necessários.
module.exports = { // Adaptado de 'export default' para Node.js
  plugins: {
    '@tailwindcss/postcss': {}, // Esta é a linha CRÍTICA para a correção do erro
    autoprefixer: {}, // Habilita o Autoprefixer
  },
};