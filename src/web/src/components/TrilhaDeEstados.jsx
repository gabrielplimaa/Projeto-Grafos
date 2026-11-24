// [IA] Claude – trilha de estados: um segmento por passo, com a cor da camada do estado.
// Mostra de relance quando o percurso muda de camada (coleta de chave) e permite pular para um passo.
// Os segmentos dividem a largura do painel, então a trilha nunca passa da borda, mesmo no m08.
import { nomeCamada, textoChaves } from "../dados.js";

const MUITOS_PASSOS = 80;          // a partir daqui, segmentos colados (sem espaço entre eles)
const DISTANCIA_MINIMA = 0.07;     // fração da trilha entre duas marcas com texto, para não se sobreporem

export default function TrilhaDeEstados({ seq, passo, cores, camada, aoEscolher }) {
  if (seq.length < 2) return null;
  const k = Math.min(passo, seq.length - 1);
  const denso = seq.length > MUITOS_PASSOS;

  // Onde o percurso muda de camada; só ganha texto a marca longe o bastante da anterior com texto
  // Num grupo de coletas seguidas, a marca com texto mostra o intervalo, por exemplo "a–abcd".
  const marcas = [];
  let comTextoAtual = null;
  seq.forEach((p, n) => {
    if (n === 0 || textoChaves(p.chaves) === textoChaves(seq[n - 1].chaves)) return;
    const camadaNova = nomeCamada(textoChaves(p.chaves));
    const perto = comTextoAtual && (n - comTextoAtual.n) / seq.length < DISTANCIA_MINIMA;
    if (perto) {
      // a marca do grupo passa a mostrar o intervalo; esta coleta não ganha marca própria
      comTextoAtual.texto = `${comTextoAtual.primeira}–${camadaNova}`;
    } else {
      comTextoAtual = { n, comTexto: true, camada: camadaNova, primeira: camadaNova, texto: camadaNova };
      marcas.push(comTextoAtual);
    }
  });

  return (
    <div className="trilha" aria-label="Trilha de estados do percurso">
      <div className="trilha-marcas" aria-hidden="true">
        {marcas.map(({ n, texto }) => (
          <span key={n} className="trilha-marca"
                style={{ left: `${(n / seq.length) * 100}%` }} title={`A partir do passo ${n}: camada ${texto}`}>
            {texto}
          </span>
        ))}
      </div>
      <div className={`trilha-faixa${denso ? " densa" : ""}`}
           style={{ gridTemplateColumns: `repeat(${seq.length}, minmax(0, 1fr))` }}>
        {seq.map((p, n) => {
          const c = textoChaves(p.chaves);
          const apagado = camada !== "todas" && c !== camada;
          return (
            <button
              key={n}
              type="button"
              tabIndex={-1}
              className={`trilha-passo${n === k ? " atual" : ""}${n > k ? " futuro" : ""}${apagado ? " apagado" : ""}`}
              style={{ "--cor": cores.get(c) }}
              title={`Passo ${n}: ${p.rotulo}`}
              aria-label={`Ir para o passo ${n}`}
              onClick={() => aoEscolher(n)}
            />
          );
        })}
      </div>
    </div>
  );
}
