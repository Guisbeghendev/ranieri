const postcss = require('postcss');
const tailwindcss = require('@tailwindcss/postcss');
const autoprefixer = require('autoprefixer');
const fs = require('fs');
const path = require('path');

// Caminho de entrada do CSS
const inputPath = path.join(__dirname, 'static', 'css', 'main.css');

// Gera um nome de arquivo único baseado no timestamp atual.
// Isso garante que o navegador sempre ignore o cache antigo.
const timestamp = Math.floor(Date.now() / 1000);
const outputFileName = `style-${timestamp}.css`;
const outputPath = path.join(__dirname, 'static', 'css', outputFileName);

// O nome do arquivo que vai guardar o nome do build mais recente.
const lastBuildFilePath = path.join(__dirname, 'static', 'css', 'last_build.txt');

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

        // Salva o nome do arquivo gerado em um arquivo de texto.
        // O projeto Django irá ler este arquivo para saber qual CSS carregar.
        fs.writeFileSync(lastBuildFilePath, outputFileName);
        console.log('Nome do arquivo de build salvo em: static/css/last_build.txt');
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
