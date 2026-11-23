"""Gera out/parte1/labirinto_interativo.html a partir dos resultados do grupo.

Este módulo só faz IO e formatação: ele NÃO calcula caminhos, custos, status nem armadilhas.
Quem decide tudo isso é o código do grupo (estados.py e algorithms.py).

Uso (exemplo do formato esperado):

    from src.labirinto_interativo import execucao_ok, execucao_status, gerar_html

    mapas = {
        "m04_esteiras": {
            "grade": linhas_do_mapa,                     # saída de ler_mapa()
            "execucoes": {
                "BFS":      execucao_ok(caminho_bfs, custos_bfs),
                "Dijkstra": execucao_ok(caminho_dij, custos_dij),
            },
            "armadilhas": estados_armadilha,             # opcional: lista de estados
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
- bonus: conjunto de bônus consumidos, como posições (i, j) das casas "+" ou já como
  números. As posições são numeradas aqui, de 0 em diante, em ordem de leitura
  (linha, depois coluna), como pede o enunciado.
- custos: dict estado -> custo acumulado (ex.: as distâncias devolvidas pelo algoritmo)
  ou lista com um custo por estado do caminho.
"""

# [IA] Claude – sintaxe de IO: conversão dos estados para JSON, numeração dos bônus
# para o rótulo e injeção no template HTML.
import json
from pathlib import Path
from src.graphs.estados import (
    numerar_bonus,
    rotulo,
    _desmontar_estado as _desmontar,
    _numeros_dos_bonus,
)

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


def passo(estado, custo):
    """Converte um estado do grafo do grupo em um passo do player."""
    pos, chaves, bonus = _desmontar(estado)
    return {
        "pos": [int(pos[0]), int(pos[1])],
        "chaves": _texto_chaves(chaves),
        "bonus": [b if isinstance(b, int) else [int(b[0]), int(b[1])] for b in bonus],
        "custo": _numero_json(custo),
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


def _completar(p, numeros, grade, onde):
    """Numera os bônus do passo, monta o rótulo e confere que a casa existe e não é parede."""
    i, j = p["pos"]
    if not (0 <= i < len(grade) and 0 <= j < len(grade[0])) or grade[i][j] == "#":
        raise ValueError(f"Passo fora do mapa ou em parede em {onde}: ({i},{j})")
    p["bonus"] = _numeros_dos_bonus(p["bonus"], numeros)
    texto_chaves = p["chaves"] or "-"
    p["rotulo"] = f"({i},{j})|{texto_chaves}|{{{','.join(str(b) for b in p['bonus'])}}}"
    return p


def _preparar_mapa(nome, mapa):
    grade = mapa.get("grade")
    if not grade or any(len(linha) != len(grade[0]) for linha in grade):
        raise ValueError(f"Grade ausente ou não retangular no mapa {nome}")
    if not mapa.get("execucoes"):
        raise ValueError(f"Mapa {nome} sem execuções")
    numeros = numerar_bonus(grade)
    execucoes = {}
    for alg, execucao in mapa["execucoes"].items():
        if execucao.get("status") not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido em {nome}/{alg}")
        nova = dict(execucao)
        for chave in ("passos", "ciclo"):
            if chave in execucao:
                nova[chave] = [_completar(dict(p), numeros, grade, f"{nome}/{alg}") for p in execucao[chave]]
        execucoes[alg] = nova
    armadilhas = [_completar(passo(e, None), numeros, grade, f"{nome}/armadilhas")
                  for e in mapa.get("armadilhas") or []]
    return {"grade": list(grade), "execucoes": execucoes, "armadilhas": armadilhas}


def gerar_html(mapas, saida=SAIDA_PADRAO):
    """Escreve o HTML interativo com os dados embutidos (abre offline, sem servidor)."""
    if not mapas:
        raise ValueError("Nenhum mapa para exportar")
    dados = {"mapas": {nome: _preparar_mapa(nome, m) for nome, m in mapas.items()}}
    texto_json = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    if MARCADOR not in template:
        raise ValueError("Marcador de dados não encontrado no template")
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(template.replace(MARCADOR, texto_json), encoding="utf-8")
    return saida
