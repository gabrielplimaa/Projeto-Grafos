// [IA] Claude – modo claro e escuro: lê e grava a preferência e aplica no <html>.
const CHAVE = "labirinto-tema";

// Na primeira abertura, segue o modo do sistema; depois, a última escolha da pessoa.
export function temaInicial() {
  try {
    const salvo = localStorage.getItem(CHAVE);
    if (salvo === "claro" || salvo === "escuro") return salvo;
  } catch { /* navegador sem armazenamento (ex.: arquivo aberto em modo restrito) */ }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
}

export function aplicarTema(tema) {
  document.documentElement.dataset.tema = tema;
  try { localStorage.setItem(CHAVE, tema); } catch { /* sem armazenamento: só não lembra a escolha */ }
}
