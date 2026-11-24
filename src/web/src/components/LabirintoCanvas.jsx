// [IA] Claude – sintaxe de canvas e React: desenha a grade, as armadilhas, o rastro e a posição atual.
import { useEffect, useRef, useState } from "react";
import { CONFIG } from "../config.js";
import { textoChaves } from "../dados.js";

// Acompanha a largura disponível para o canvas (o tamanho das casas depende dela)
function useLargura(ref) {
  const [largura, setLargura] = useState(0);
  useEffect(() => {
    const observador = new ResizeObserver(([entrada]) => setLargura(entrada.contentRect.width));
    observador.observe(ref.current);
    return () => observador.disconnect();
  }, [ref]);
  return largura;
}

export default function LabirintoCanvas({ grade, seq, passo, cores, camada, armadilhas, realcar }) {
  const caixa = useRef(null);
  const canvas = useRef(null);
  const largura = useLargura(caixa);

  useEffect(() => {
    if (!largura) return;
    const linhas = grade.length, colunas = grade[0].length;
    const t = Math.max(CONFIG.tamanhoMinCelula, Math.min(CONFIG.tamanhoMaxCelula, Math.floor(largura / colunas)));
    const escala = window.devicePixelRatio || 1;          // nitidez em telas de alta densidade
    const c = canvas.current;
    c.width = colunas * t * escala; c.height = linhas * t * escala;
    c.style.width = `${colunas * t}px`; c.style.height = `${linhas * t}px`;
    const ctx = c.getContext("2d");
    ctx.setTransform(escala, 0, 0, escala, 0, 0);
    const naCamada = (p) => camada === "todas" || textoChaves(p.chaves) === camada;

    // 1. Terreno: uma cor por símbolo; o símbolo é escrito quando a casa é grande o bastante
    ctx.font = `600 ${Math.floor(t * 0.5)}px system-ui, sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    for (let i = 0; i < linhas; i++) {
      for (let j = 0; j < colunas; j++) {
        const s = grade[i][j];
        ctx.fillStyle = CONFIG.coresTerreno[s] || "#ffffff";
        ctx.fillRect(j * t, i * t, t, t);
        if (s !== "#") {                                     // linha fina entre casas livres
          ctx.strokeStyle = "rgba(29, 43, 58, 0.08)"; ctx.lineWidth = 1;
          ctx.strokeRect(j * t + 0.5, i * t + 0.5, t - 1, t - 1);
        }
        if (t >= 14 && s !== "#" && s !== ".") {
          ctx.fillStyle = "rgba(29, 43, 58, 0.75)";
          ctx.fillText(s, j * t + t / 2, i * t + t / 2 + 1);
        }
      }
    }

    // 2. Estados-armadilha da camada escolhida: hachura diagonal e contorno, uma vez por casa
    if (realcar) {
      const casas = new Set(armadilhas.filter(naCamada).map((a) => a.pos.join(",")));
      for (const casa of casas) {
        const [i, j] = casa.split(",").map(Number);
        const x = j * t, y = i * t;
        ctx.save();
        ctx.beginPath(); ctx.rect(x, y, t, t); ctx.clip();
        ctx.strokeStyle = CONFIG.corArmadilha; ctx.lineWidth = 1;
        ctx.beginPath();
        for (let d = -t; d < t; d += Math.max(3, t / 4)) { ctx.moveTo(x + d, y + t); ctx.lineTo(x + d + t, y); }
        ctx.stroke();
        ctx.restore();
        ctx.strokeStyle = CONFIG.corArmadilha; ctx.lineWidth = 2;
        ctx.strokeRect(x + 1, y + 1, t - 2, t - 2);
      }
    }

    if (!seq.length) return;
    const k = Math.min(passo, seq.length - 1);
    const centro = (p) => [p.pos[1] * t + t / 2, p.pos[0] * t + t / 2];

    // 3. Rastro até o passo atual; cada trecho tem a cor da camada do estado de destino
    ctx.lineWidth = Math.max(2.5, t / 4.5);
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    for (let n = 1; n <= k; n++) {
      const [x0, y0] = centro(seq[n - 1]);
      const [x1, y1] = centro(seq[n]);
      ctx.globalAlpha = naCamada(seq[n]) ? 1 : CONFIG.opacidadeForaDaCamada;
      ctx.strokeStyle = cores.get(textoChaves(seq[n].chaves));
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // 4. Início (anel) e posição atual (disco branco com borda)
    const [xi, yi] = centro(seq[0]);
    ctx.strokeStyle = "#1D2B3A"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(xi, yi, Math.max(3, t * 0.22), 0, 2 * Math.PI); ctx.stroke();
    const [x, y] = centro(seq[k]);
    ctx.fillStyle = "#ffffff"; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(x, y, Math.max(4, t * 0.34), 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
  }, [largura, grade, seq, passo, cores, camada, armadilhas, realcar]);

  return (
    <div className="mapa" ref={caixa}>
      <canvas ref={canvas} role="img" aria-label="Mapa do labirinto com o percurso até o passo atual" />
    </div>
  );
}
