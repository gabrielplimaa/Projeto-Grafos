"""Gera out/parte1/labirinto_interativo.html a partir dos resultados do grupo.

Este módulo só faz IO e formatação: ele NÃO calcula caminhos, custos nem status.
Quem decide o caminho de cada algoritmo é o código do grupo (estados.py e algorithms.py).

Uso (exemplo do formato esperado):

    from src.labirinto_interativo import execucao_ok, execucao_status, gerar_html

    mapas = {
        "m02_uma_chave": {
            "grade": linhas_do_mapa,                     # saída de ler_mapa()
            "execucoes": {
                "BFS":      execucao_ok(caminho_bfs, custos_bfs),
                "Dijkstra": execucao_ok(caminho_dij, custos_dij),
            },
        },
        "m06_fonte": {
            "grade": linhas_m06,
            "execucoes": {
                "Dijkstra":     execucao_status("recusado", "peso negativo encontrado"),
                "Bellman-Ford": execucao_status("ciclo_negativo", "ciclo detectado", ciclo=estados_do_ciclo),
            },
        },
    }
    gerar_html(mapas)

- caminho: lista de estados na ordem do percurso, no formato do grafo de estados
  do grupo: ((i, j), chaves) ou ((i, j), chaves, bonus).
- custos: dict estado -> custo acumulado (ex.: as distâncias devolvidas pelo algoritmo)
  ou lista com um custo por estado do caminho.
"""

# [IA] Claude – sintaxe de IO: conversão dos estados para JSON e injeção no template HTML.

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent
TEMPLATE = PASTA / "templates" / "labirinto_template.html"
SAIDA_PADRAO = Path("out/parte1/labirinto_interativo.html")
MARCADOR = "/*__DADOS__*/null"
STATUS_VALIDOS = {"ok", "sem_solucao", "recusado", "ciclo_negativo"}


def _texto_chaves(chaves):
    return "".join(sorted(chaves)) if chaves else ""


def _numero_json(valor):
    if valor is None or valor == float("inf") or valor == float("-inf"):
        return None
    return valor


def rotulo(estado):
    """Rótulo no formato do enunciado: (linha,coluna)|chaves|{bônus}."""
    pos, chaves, bonus = _desmontar(estado)
    texto_chaves = _texto_chaves(chaves) or "-"
    texto_bonus = "{" + ",".join(str(b) for b in sorted(bonus)) + "}"
    return f"({pos[0]},{pos[1]})|{texto_chaves}|{texto_bonus}"


def _desmontar(estado):
    if len(estado) == 3:
        pos, chaves, bonus = estado
    elif len(estado) == 2:
        pos, chaves = estado
        bonus = ()
    else:
        raise ValueError(f"Estado em formato inesperado: {estado!r}")
    return pos, chaves, bonus


def passo(estado, custo):
    """Converte um estado do grafo do grupo em um passo do player."""
    pos, chaves, bonus = _desmontar(estado)
    return {
        "pos": [int(pos[0]), int(pos[1])],
        "chaves": _texto_chaves(chaves),
        "bonus": sorted(bonus),
        "custo": _numero_json(custo),
        "rotulo": rotulo(estado),
    }


def _lista_de_passos(estados, custos):
    if custos is None:
        return [passo(e, None) for e in estados]
    if isinstance(custos, dict):
        return [passo(e, custos.get(e)) for e in estados]
    if len(custos) != len(estados):
        raise ValueError("A lista de custos precisa ter um valor por estado do caminho")
    return [passo(e, c) for e, c in zip(estados, custos)]


def execucao_ok(caminho, custos=None, mensagem=""):
    """Execução com caminho encontrado. O caminho vem do código do grupo."""
    if not caminho:
        raise ValueError("Caminho vazio: use execucao_status('sem_solucao', ...)")
    return {"status": "ok", "mensagem": mensagem, "passos": _lista_de_passos(caminho, custos)}


def execucao_status(status, mensagem="", ciclo=None, custos_ciclo=None):
    """Execução sem caminho: 'sem_solucao', 'recusado' ou 'ciclo_negativo' (com o ciclo opcional)."""
    if status not in STATUS_VALIDOS - {"ok"}:
        raise ValueError(f"Status inválido: {status!r}")
    execucao = {"status": status, "mensagem": mensagem, "passos": []}
    if ciclo:
        execucao["ciclo"] = _lista_de_passos(ciclo, custos_ciclo)
    return execucao


def _validar(mapas):
    if not mapas:
        raise ValueError("Nenhum mapa para exportar")
    for nome, mapa in mapas.items():
        grade = mapa.get("grade")
        if not grade or any(len(linha) != len(grade[0]) for linha in grade):
            raise ValueError(f"Grade ausente ou não retangular no mapa {nome}")
        if not mapa.get("execucoes"):
            raise ValueError(f"Mapa {nome} sem execuções")
        for alg, execucao in mapa["execucoes"].items():
            if execucao.get("status") not in STATUS_VALIDOS:
                raise ValueError(f"Status inválido em {nome}/{alg}")
            for p in execucao.get("passos", []) + execucao.get("ciclo", []):
                i, j = p["pos"]
                if not (0 <= i < len(grade) and 0 <= j < len(grade[0])) or grade[i][j] == "#":
                    raise ValueError(f"Passo fora do mapa ou em parede em {nome}/{alg}: {p['rotulo']}")


def gerar_html(mapas, saida=SAIDA_PADRAO):
    """Escreve o HTML interativo com os dados embutidos (abre offline, sem servidor)."""
    _validar(mapas)
    dados = {"mapas": {nome: {"grade": list(m["grade"]), "execucoes": m["execucoes"]}
                       for nome, m in mapas.items()}}
    texto_json = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    if MARCADOR not in template:
        raise ValueError("Marcador de dados não encontrado no template")
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(template.replace(MARCADOR, texto_json), encoding="utf-8")
    return saida
