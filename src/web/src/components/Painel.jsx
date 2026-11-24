// [IA] Claude – painel de um algoritmo: status, mapa, trilha de estados e leitura do estado atual.
import LabirintoCanvas from "./LabirintoCanvas.jsx";
import TrilhaDeEstados from "./TrilhaDeEstados.jsx";
import { STATUS, nomeCamada, sequencia, textoBonus, textoChaves } from "../dados.js";

export default function Painel({ nome, execucao, mapa, passo, cores, camada, realcar, rotulosArmadilha, aoEscolher }) {
  const seq = sequencia(execucao);
  const k = Math.min(passo, seq.length - 1);
  const p = k >= 0 ? seq[k] : null;
  const status = STATUS[execucao.status] ?? { texto: execucao.status, classe: "" };
  const ehCiclo = execucao.status === "ciclo_negativo";

  return (
    <section className="painel" aria-label={`Algoritmo ${nome}`}>
      <header className="painel-topo">
        <h2>{nome}</h2>
        <span className={`status ${status.classe}`}>{status.texto}</span>
      </header>
      {execucao.mensagem && <p className="painel-mensagem">{execucao.mensagem}</p>}

      <LabirintoCanvas grade={mapa.grade} seq={seq} passo={passo} cores={cores} camada={camada}
                       armadilhas={mapa.armadilhas || []} realcar={realcar} />
      <TrilhaDeEstados seq={seq} passo={passo} cores={cores} camada={camada} aoEscolher={aoEscolher} />

      {p ? (
        <div className="leitura">
          <div className="leitura-estado">
            <span className="leitura-nome">Estado</span>
            <code>{p.rotulo}</code>
          </div>
          <dl>
            <div><dt>Passo</dt><dd>{k} de {seq.length - 1}</dd></div>
            <div><dt>Posição</dt><dd>({p.pos[0]}, {p.pos[1]})</dd></div>
            <div>
              <dt>Chaves</dt>
              <dd><span className="chip-camada" style={{ "--cor": cores.get(textoChaves(p.chaves)) }}>{nomeCamada(textoChaves(p.chaves))}</span></dd>
            </div>
            <div><dt>Bônus consumidos</dt><dd>{textoBonus(p.bonus)}</dd></div>
            <div><dt>{ehCiclo ? "Custo no ciclo" : "Custo acumulado"}</dt><dd>{p.custo ?? "—"}</dd></div>
            <div><dt>Estado-armadilha</dt><dd>{rotulosArmadilha.has(p.rotulo) ? "sim" : "não"}</dd></div>
          </dl>
        </div>
      ) : (
        <p className="painel-vazio">
          {execucao.status === "recusado" && "Sem percurso para animar: o algoritmo recusou este grafo."}
          {execucao.status === "sem_solucao" && "Sem percurso para animar: nenhum estado em G é alcançável a partir do início."}
          {execucao.status === "ciclo_negativo" && "O ciclo negativo não foi exportado para este mapa."}
        </p>
      )}
    </section>
  );
}
