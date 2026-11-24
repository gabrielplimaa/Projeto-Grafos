// [IA] Claude – coluna de controles: algoritmos, camada, armadilhas e legenda.
import { CONFIG, NOMES_TERRENO } from "../config.js";
import { STATUS, nomeCamada, resumo, textoChaves } from "../dados.js";

export default function BarraLateral({ mapa, algoritmos, marcados, aoMarcar, camadas, cores, camada, aoTrocarCamada,
                                       realcar, aoRealcar }) {
  const armadilhas = mapa.armadilhas || [];
  const naCamada = (a) => camada === "todas" || textoChaves(a.chaves) === camada;
  const visiveis = armadilhas.filter(naCamada);
  const casas = new Set(visiveis.map((a) => a.pos.join(","))).size;
  const texto = mapa.grade.join("");
  // chaves, portas e esteiras aparecem uma vez na legenda, se houver qualquer uma no mapa
  const GRUPOS = { a: /[abcd]/, A: /[ABCD]/, ">": /[<>^v]/ };
  const presente = (s) => (GRUPOS[s] ? GRUPOS[s].test(texto) : texto.includes(s));

  return (
    <aside className="lateral">
      <section className="grupo">
        <h3>Algoritmos</h3>
        <p className="dica">Marque mais de um para comparar lado a lado.</p>
        <ul className="lista-algoritmos">
          {algoritmos.map((nome) => {
            const execucao = mapa.execucoes[nome];
            const status = STATUS[execucao.status] ?? { classe: "" };
            return (
              <li key={nome}>
                <label className="algoritmo">
                  <input type="checkbox" checked={marcados.includes(nome)} onChange={() => aoMarcar(nome)} />
                  <span className="algoritmo-texto">
                    <span className="algoritmo-nome">
                      <span className={`ponto ${status.classe}`} aria-hidden="true" />{nome}
                    </span>
                    <span className="algoritmo-resumo">{resumo(execucao)}</span>
                  </span>
                </label>
              </li>
            );
          })}
        </ul>
      </section>

      <section className="grupo">
        <h3>Camada</h3>
        <p className="dica">Cada camada é um conjunto de chaves.</p>
        <div className="chips" role="radiogroup" aria-label="Camada">
          {["todas", ...camadas].map((c) => (
            <button key={c} type="button" role="radio" aria-checked={camada === c}
                    className={`chip${camada === c ? " ativo" : ""}`} onClick={() => aoTrocarCamada(c)}>
              {c !== "todas" && <span className="amostra" style={{ background: cores.get(c) }} aria-hidden="true" />}
              {c === "todas" ? "todas" : nomeCamada(c)}
            </button>
          ))}
        </div>
      </section>

      <section className="grupo">
        <h3>Estados-armadilha</h3>
        <label className="interruptor">
          <input type="checkbox" checked={realcar} onChange={(e) => aoRealcar(e.target.checked)} />
          <span>Realçar no mapa</span>
        </label>
        <p className="dica">
          {armadilhas.length === 0
            ? "Nenhum estado-armadilha neste mapa."
            : `${visiveis.length} ${visiveis.length === 1 ? "estado" : "estados"} em ${casas} ${casas === 1 ? "casa" : "casas"}` +
              (camada === "todas" ? ", somando todas as camadas." : `, na camada ${nomeCamada(camada)}.`)}
        </p>
      </section>

      <section className="grupo">
        <h3>Legenda</h3>
        <ul className="legenda">
          {NOMES_TERRENO.filter(([s]) => presente(s))
            .map(([s, nome]) => (
              <li key={s}><span className="amostra" style={{ background: CONFIG.coresTerreno[s] }} aria-hidden="true" />{nome}</li>
            ))}
          <li><span className="amostra hachura" aria-hidden="true" />estado-armadilha</li>
        </ul>
      </section>
    </aside>
  );
}
