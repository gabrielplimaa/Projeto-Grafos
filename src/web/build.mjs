// [IA] Claude – sintaxe do build com esbuild: junta React, os componentes e o CSS num único
// template HTML, sem dependências externas, para o labirinto_interativo.html abrir offline.
//
// Uso (dentro de src/web):  npm install  e depois  npm run build
// Saída: ../templates/labirinto_template.html (o mesmo template que src/labirinto_interativo.py lê).

import { build } from "esbuild";
import { readFileSync, writeFileSync } from "node:fs";

const resultado = await build({
  entryPoints: ["src/main.jsx"],
  bundle: true,
  minify: true,
  format: "iife",
  jsx: "automatic",
  target: ["es2020"],
  define: { "process.env.NODE_ENV": '"production"' },
  legalComments: "none",
  write: false,
});

const js = resultado.outputFiles[0].text;
const css = readFileSync("src/estilos.css", "utf8");

// O gerador Python troca este marcador pelo JSON com os resultados do grupo.
const MARCADOR = "/*__DADOS__*/null";
for (const [nome, proibido] of [["marcador", MARCADOR], ["fim de script", "</script"], ["declaração de DADOS", "const DADOS = "]]) {
  if (js.includes(proibido)) throw new Error(`O bundle contém ${nome}; o template ficaria inválido.`);
}

const html = `<!DOCTYPE html>
<!-- [IA] Claude – template gerado por src/web/build.mjs a partir dos componentes React em src/web/src.
     Não edite este arquivo à mão: edite src/web/src e rode "npm run build" em src/web.
     Os dados (caminhos, custos, status, armadilhas) são calculados pelo código do grupo e
     injetados por src/labirinto_interativo.py no lugar do marcador abaixo. -->
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labirinto interativo</title>
<script>
// Aplica o tema antes de desenhar a página, para não piscar no modo errado
try {
  var t = localStorage.getItem("labirinto-tema");
  if (t !== "claro" && t !== "escuro") t = matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
  document.documentElement.dataset.tema = t;
} catch (e) {}
</script>
<style>
${css}
</style>
</head>
<body>
<div id="raiz"></div>
<script>
const DADOS = ${MARCADOR};
</script>
<script>
${js}
</script>
</body>
</html>
`;

writeFileSync("../templates/labirinto_template.html", html, "utf8");
console.log(`Template gerado: ../templates/labirinto_template.html (${(html.length / 1024).toFixed(0)} KB)`);
