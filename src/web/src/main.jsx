// [IA] Claude – ponto de entrada do React: lê os dados injetados pelo Python e monta o App.
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

// DADOS é declarado num <script> anterior do template, preenchido por gerar_html.
const dados = typeof DADOS !== "undefined" ? DADOS : null;
createRoot(document.getElementById("raiz")).render(<App dados={dados} />);
