import csv
from src.graphs.algorithms import bfs
from src.graphs.graph import Grafo


def test_bfs_niveis_e_exportacao(tmp_path):
    # Grafo pequeno calculado à mão:
    # A -> B (nível 1), A -> C (nível 1), B -> D (nível 2), C -> D (nível 2), D -> E (nível 3)
    grafo = Grafo()
    for v in ["A", "B", "C", "D", "E"]:
        grafo.adicionar_no(v)
    grafo.ligar("A", "B", 1)
    grafo.ligar("A", "C", 1)
    grafo.ligar("B", "D", 1)
    grafo.ligar("C", "D", 1)
    grafo.ligar("D", "E", 1)

    distancias, antecessores = bfs(grafo, "A")

    assert distancias == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 3}
    assert antecessores["E"] == "D"

    # Exportação segura em pasta temporária (tmp_path) sem alterar out/parte1/
    arquivo_temp = tmp_path / "resultado_bfs.csv"
    with open(arquivo_temp, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["vertice", "nivel"])
        for v, nivel in distancias.items():
            writer.writerow([v, nivel])

    assert arquivo_temp.exists()