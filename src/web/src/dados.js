// [IA] Claude – funções de apoio do player. Nenhuma delas calcula caminho: só leem o que o
// código do grupo gravou em DADOS (src/labirinto_interativo.py).

import { CONFIG } from "./config.js";

export const textoChaves = (chaves) => (chaves && chaves.length ? chaves : "-");
export const nomeCamada = (camada) => (camada === "-" ? "sem chave" : camada);
export const textoBonus = (bonus = []) => "{" + bonus.join(",") + "}";

// O que animar numa execução: o caminho (ok) ou o ciclo negativo (Bellman-Ford)
export function sequencia(execucao) {
  if (execucao.status === "ok") return execucao.passos || [];
  if (execucao.status === "ciclo_negativo") return execucao.ciclo || [];
  return [];
}

// Todas as camadas (conjuntos de chaves) que aparecem nos percursos e nas armadilhas do mapa,
// em ordem: sem chave, depois pelo número de chaves, depois alfabética.
export function camadasDoMapa(mapa) {
  const vistas = new Set();
  for (const execucao of Object.values(mapa.execucoes)) {
    for (const p of [...(execucao.passos || []), ...(execucao.ciclo || [])]) vistas.add(textoChaves(p.chaves));
  }
  for (const a of mapa.armadilhas || []) vistas.add(textoChaves(a.chaves));
  const tamanho = (c) => (c === "-" ? 0 : c.length);
  return [...vistas].sort((x, y) => tamanho(x) - tamanho(y) || x.localeCompare(y));
}

// A mesma camada tem a mesma cor em todos os painéis e na legenda
export function coresPorCamada(camadas) {
  const cores = new Map();
  camadas.forEach((c, k) => cores.set(c, CONFIG.coresCamadas[k % CONFIG.coresCamadas.length]));
  return cores;
}

export const STATUS = {
  ok: { texto: "caminho encontrado", classe: "ok" },
  recusado: { texto: "recusado", classe: "recusado" },
  sem_solucao: { texto: "sem solução", classe: "sem-solucao" },
  ciclo_negativo: { texto: "ciclo negativo", classe: "ciclo" },
};

// Resumo curto de uma execução para a lista de algoritmos
export function resumo(execucao) {
  const seq = sequencia(execucao);
  if (!seq.length) return STATUS[execucao.status]?.texto ?? execucao.status;
  const custo = seq[seq.length - 1].custo;
  const passos = seq.length - 1;
  if (execucao.status === "ciclo_negativo") return `ciclo de ${passos} arcos, custo ${custo}`;
  return `${passos} passos, custo ${custo ?? "—"}`;
}
