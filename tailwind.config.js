// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = { // Adaptado de 'export default' para Node.js
  content: [
    // Estes são os caminhos onde o Tailwind vai PROCURAR por classes que você usar nos seus HTMLs.
    // Como você ainda não tem HTMLs prontos, ele não encontrará classes AGORA,
    // o que é normal. No FUTURO, quando tiver HTMLs, ele vai escanear essas pastas.
    "./templates/**/*.html", // Para templates na raiz do seu projeto Django (ex: proj001-ranieri/templates/...)
    "./*/templates/**/*.html", // Para templates dentro de apps Django (ex: proj001-ranieri/myapp/templates/...)
    "./ranieri_project/**/*.html", // Para qualquer HTML dentro da pasta ranieri_project
    // Se você usa classes Tailwind em arquivos JavaScript/TypeScript (no frontend), adicione os caminhos aqui:
    // "./ranieri_project/**/*.{js,ts,jsx,tsx}",
    // Adicione o caminho para os arquivos do Preline UI
    './node_modules/preline/preline.js',
  ],
  theme: {
    extend: {
      // SUAS CORES PERSONALIZADAS ESTÃO AQUI, CONFORME SOLICITADO.
      // Para Tailwind CSS v4.x.x, a forma PREFERENCIAL de gerar classes de utilidade (ex: bg-roxo1)
      // a partir dessas cores é definindo-as no seu arquivo CSS principal (ex: main.css)
      // dentro do bloco @theme { ... }.
      // No entanto, defini-las aqui as torna disponíveis como variáveis CSS (ex: var(--tw-roxo1))
      // e para outras extensões de tema ou plugins.
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
      }
    },
  },
  plugins: [
          require('preline/plugin'), // Adicione o plugin do Preline UI aqui
  ],
};