// [IA] Claude – componente principal: guarda o estado da tela (mapa, algoritmos, passo, animação,
// camada) e repassa para a barra lateral, os painéis e a barra de reprodução.
import { useEffect, useMemo, useState } from "react";
import BarraLateral from "./components/BarraLateral.jsx";
import Painel from "./components/Painel.jsx";
import Transporte from "./components/Transporte.jsx";
import { camadasDoMapa, coresPorCamada, sequencia } from "./dados.js";
import { aplicarTema, temaInicial } from "./tema.js";

export default function App({ dados }) {
  if (!dados) {
    return (
      <main className="sem-dados">
        <h1>Labirinto interativo</h1>
        <p>Este arquivo ainda não tem dados. Gere a versão com os mapas rodando, na raiz do projeto:</p>
        <code>python -m src.cli --interactive --out ./out/parte1/</code>
      </main>
    );
  }
  return <Player dados={dados} />;
}

function Player({ dados }) {
  const nomesMapas = Object.keys(dados.mapas);
  const [nomeMapa, setNomeMapa] = useState(nomesMapas[0]);
  const mapa = dados.mapas[nomeMapa];
  const algoritmos = Object.keys(mapa.execucoes);

  const [marcados, setMarcados] = useState(algoritmos.slice(0, 1));
  const [passo, setPasso] = useState(0);
  const [tocando, setTocando] = useState(false);
  const [velocidade, setVelocidade] = useState(4);
  const [camada, setCamada] = useState("todas");
  const [realcar, setRealcar] = useState(true);
  const [tema, setTema] = useState(temaInicial);
  useEffect(() => aplicarTema(tema), [tema]);

  const camadas = useMemo(() => camadasDoMapa(mapa), [mapa]);
  const cores = useMemo(() => coresPorCamada(camadas), [camadas]);
  const rotulosArmadilha = useMemo(() => new Set((mapa.armadilhas || []).map((a) => a.rotulo)), [mapa]);

  // O fim da barra de passos é o maior percurso entre os algoritmos marcados
  const total = Math.max(0, ...marcados.map((alg) => sequencia(mapa.execucoes[alg]).length - 1));
  const passoVisivel = Math.min(passo, total);          // desmarcar um algoritmo pode encurtar o total
  const irPara = (n) => { setTocando(false); setPasso(Math.max(0, Math.min(n, total))); };

  function trocarMapa(nome) {
    setNomeMapa(nome);
    setMarcados(Object.keys(dados.mapas[nome].execucoes).slice(0, 1));
    setPasso(0); setTocando(false); setCamada("todas");
  }
  const marcar = (alg) =>
    setMarcados((atuais) => (atuais.includes(alg) ? atuais.filter((a) => a !== alg) : algoritmos.filter((a) => atuais.includes(a) || a === alg)));

  function tocarOuPausar() {
    if (tocando) { setTocando(false); return; }
    if (passoVisivel >= total) setPasso(0);                     // no fim, recomeça do início
    setTocando(true);
  }

  // Animação: avança um passo a cada 1000 / velocidade ms e para sozinha no fim
  useEffect(() => {
    if (!tocando) return;
    const id = setInterval(() => {
      setPasso((p) => {
        if (p >= total) { setTocando(false); return p; }
        return p + 1;
      });
    }, 1000 / velocidade);
    return () => clearInterval(id);
  }, [tocando, velocidade, total]);

  // Atalhos de teclado (fora de campos de formulário, que já usam as setas)
  useEffect(() => {
    function tecla(e) {
      const alvo = e.target;
      // barras deslizantes e listas já usam as setas; caixas de seleção e botões não
      const usaSetas = alvo.tagName === "SELECT" || alvo.tagName === "TEXTAREA" ||
        (alvo.tagName === "INPUT" && !["checkbox", "radio"].includes(alvo.type));
      if (usaSetas) return;
      if (e.key === " ") {
        // Espaço num botão ou numa caixa de seleção mantém o comportamento normal dela
        if (alvo.tagName === "BUTTON" || alvo.tagName === "INPUT") return;
        e.preventDefault(); tocarOuPausar();
      }
      else if (e.key === "ArrowRight") { e.preventDefault(); irPara(passoVisivel + 1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); irPara(passoVisivel - 1); }
      else if (e.key === "Home") { e.preventDefault(); irPara(0); }
      else if (e.key === "End") { e.preventDefault(); irPara(total); }
    }
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  });

  return (
    <div className="pagina">
      <header className="topo">
        <h1>Labirinto interativo</h1>
        <label className="seletor-mapa">
          <span>Mapa</span>
          <select value={nomeMapa} onChange={(e) => trocarMapa(e.target.value)}>
            {nomesMapas.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
        <p className="topo-resumo">
          {mapa.grade.length} × {mapa.grade[0].length} casas, {camadas.length} {camadas.length === 1 ? "camada" : "camadas"}
        </p>
        <BotaoTema tema={tema} aoTrocar={() => setTema(tema === "escuro" ? "claro" : "escuro")} />
      </header>

      <div className="corpo">
        <BarraLateral mapa={mapa} algoritmos={algoritmos} marcados={marcados} aoMarcar={marcar}
                      camadas={camadas} cores={cores} camada={camada} aoTrocarCamada={setCamada}
                      realcar={realcar} aoRealcar={setRealcar} />
        <main className={`paineis${marcados.length > 1 ? " varios" : ""}`}>
          {marcados.length === 0 && <p className="painel-vazio">Marque um algoritmo na coluna ao lado para ver o percurso.</p>}
          {marcados.map((alg) => (
            <Painel key={alg} nome={alg} execucao={mapa.execucoes[alg]} mapa={mapa} passo={passoVisivel} cores={cores}
                    camada={camada} realcar={realcar} rotulosArmadilha={rotulosArmadilha} aoEscolher={irPara} />
          ))}
        </main>
      </div>

      <Transporte passo={passoVisivel} total={total} tocando={tocando} velocidade={velocidade}
                  aoIr={irPara} aoTocar={tocarOuPausar} aoVelocidade={setVelocidade} />
    </div>
  );
}

// Botão do topo: mostra o ícone do modo para o qual vai trocar
function BotaoTema({ tema, aoTrocar }) {
  const escuro = tema === "escuro";
  return (
    <button type="button" className="botao-tema" onClick={aoTrocar} aria-pressed={escuro}
            title={escuro ? "Mudar para o modo claro" : "Mudar para o modo escuro"}>
      <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true">
        {escuro
          ? <g fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="4.2" />
              <path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" />
            </g>
          : <path d="M20.5 14.6A8.5 8.5 0 0 1 9.4 3.5a8.5 8.5 0 1 0 11.1 11.1z" fill="currentColor" />}
      </svg>
      <span>{escuro ? "Modo claro" : "Modo escuro"}</span>
    </button>
  );
}
