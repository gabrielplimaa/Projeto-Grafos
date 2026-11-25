import json
from src.graphs.algorithms import dfs
from src.graphs.graph import Grafo


def test_dfs_classificacao_e_ciclo(tmp_path):
    # Grafo dirigido com os 4 tipos de arcos (arvore, retorno, avanco, cruzamento):
    # Ordem de vizinhos importa:
    # A -> B, A -> C
    # B -> D
    # D -> B (retorno -> ciclo)
    # A -> D (avanco: D já foi descoberto e finalizado no ramo de B)
    # C -> D (cruzamento: D já foi finalizado em outro ramo)
    grafo = Grafo()
    for v in ["A", "B", "C", "D"]:
        grafo.adicionar_no(v)
    grafo.ligar("A", "B", 1)
    grafo.ligar("A", "C", 1)
    grafo.ligar("A", "D", 1)
    grafo.ligar("B", "D", 1)
    grafo.ligar("D", "B", 1)
    grafo.ligar("C", "D", 1)

    resultado = dfs(grafo, "A")
    contagens = resultado["contagens"]

    assert resultado["tem_ciclo"] is True
    assert contagens == {"arvore": 3, "retorno": 1, "avanco": 1, "cruzamento": 1}

    # Exportação segura em pasta temporária (tmp_path)
    arquivo_temp = tmp_path / "resultado_dfs.json"
    with open(arquivo_temp, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4)

    assert arquivo_temp.exists()