// build-tailwind.js
const postcss = require('postcss');
const tailwindcss = require('@tailwindcss/postcss');
const autoprefixer = require('autoprefixer');
const fs = require('fs');
const path = require('path');

const inputPath = path.join(__dirname, 'static', 'css', 'main.css');
const outputPath = path.join(__dirname, 'static', 'css', 'style.css');

try {
    const inputCss = fs.readFileSync(inputPath, 'utf8');
    console.log('Iniciando compilação do Tailwind CSS...');
    postcss([tailwindcss, autoprefixer])
    .process(inputCss, { from: inputPath, to: outputPath })
    .then(result => {
        fs.writeFileSync(outputPath, result.css);
        if (result.map) {
            fs.writeFileSync(outputPath + '.map', result.map.toString());
        }
        console.log('Compilação do Tailwind CSS concluída com sucesso: ' + outputPath);
    })
    .catch(error => {
        console.error('Erro durante a compilação do Tailwind CSS:', error);
        if (error.codeFrame) {
            console.error(error.codeFrame);
        }
        process.exit(1);
    });
} catch (err) {
    console.error("Erro ao ler o arquivo de entrada ou iniciar:", err);
    process.exit(1);
}