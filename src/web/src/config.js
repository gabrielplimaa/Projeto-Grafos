// [IA] Claude – sintaxe JS. As cores abaixo foram escolhidas pelo grupo (ver justificativa no PDF).
// Edite aqui e rode "npm run build" em src/web para regerar o template.

export const CONFIG = {
  // Cor de cada símbolo do mapa (as mesmas de CORES_TERRENO em src/viz.py)
  coresTerreno: {
    "#": "#34495E", ".": "#ecf0f1", S: "#2ecc71", G: "#e74c3c",
    ",": "#95a5a6", "~": "#3498db",
    a: "#f1c40f", b: "#f1c40f", c: "#f1c40f", d: "#f1c40f",
    A: "#e67e22", B: "#e67e22", C: "#e67e22", D: "#e67e22",
    ">": "#dfe6e9", "<": "#dfe6e9", "^": "#dfe6e9", v: "#dfe6e9",
    "+": "#7E57C2", "*": "#C2185B",
  },
  // Uma cor por camada (conjunto de chaves), na ordem: sem chave, a, b, ..., ab, ... (as mesmas de CORES_CAMADAS)
  coresCamadas: ["#6A3D9A", "#A23B72", "#795548", "#00695C", "#827717", "#424242"],
  // Realce dos estados-armadilha: hachura e contorno
  corArmadilha: "#B71C1C",
  // Opacidade dos trechos do rastro fora da camada escolhida
  opacidadeForaDaCamada: 0.15,
  tamanhoMaxCelula: 52,
  tamanhoMinCelula: 6,
};

export const NOMES_TERRENO = [
  ["#", "parede"], [".", "chão"], ["S", "início"], ["G", "saída"], [",", "lama (custo 3)"],
  ["~", "água (custo 5)"], ["a", "chave"], ["A", "porta"], [">", "esteira"], ["+", "bônus"], ["*", "fonte"],
];
