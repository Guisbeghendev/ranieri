// postcss.config.js
// Este arquivo configura o PostCSS para usar os plugins necessários.
module.exports = {
  plugins: {
    tailwindcss: {}, // CORREÇÃO: Usar 'tailwindcss' diretamente para v4.x.x
    autoprefixer: {}, // Habilita o Autoprefixer
  },
};