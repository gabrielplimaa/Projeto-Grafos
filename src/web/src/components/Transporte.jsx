// [IA] Claude – barra de reprodução: botões, barra de passos e velocidade.
const Icone = ({ d }) => (
  <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d={d} fill="currentColor" /></svg>
);
const ICONES = {
  inicio: "M6 5h2v14H6zM20 5v14L9 12z",
  anterior: "M17 5v14L6 12z",
  tocar: "M7 5v14l12-7z",
  pausar: "M6 5h4v14H6zM14 5h4v14h-4z",
  proximo: "M7 5v14l11-7z",
  fim: "M16 5h2v14h-2zM4 5v14l11-7z",
};

export default function Transporte({ passo, total, tocando, velocidade, aoIr, aoTocar, aoVelocidade }) {
  return (
    <footer className="transporte">
      <div className="botoes">
        <button type="button" onClick={() => aoIr(0)} aria-label="Ir para o início"><Icone d={ICONES.inicio} /></button>
        <button type="button" onClick={() => aoIr(passo - 1)} aria-label="Passo anterior"><Icone d={ICONES.anterior} /></button>
        <button type="button" className="principal" onClick={aoTocar} aria-label={tocando ? "Pausar" : "Tocar"}>
          <Icone d={tocando ? ICONES.pausar : ICONES.tocar} />
        </button>
        <button type="button" onClick={() => aoIr(passo + 1)} aria-label="Próximo passo"><Icone d={ICONES.proximo} /></button>
        <button type="button" onClick={() => aoIr(total)} aria-label="Ir para o fim"><Icone d={ICONES.fim} /></button>
      </div>

      <label className="linha-tempo">
        <span className="rotulo-oculto">Passo</span>
        <input type="range" min="0" max={total} value={passo} onChange={(e) => aoIr(Number(e.target.value))} />
        <span className="contador">passo {passo} de {total}</span>
      </label>

      <label className="velocidade">
        <span>Velocidade</span>
        <input type="range" min="1" max="30" value={velocidade} onChange={(e) => aoVelocidade(Number(e.target.value))} />
        <span className="contador">{velocidade} passos/s</span>
      </label>

      <p className="atalhos">Atalhos: Espaço toca ou pausa, ← e → andam um passo, Home e End vão ao início e ao fim.</p>
    </footer>
  );
}
