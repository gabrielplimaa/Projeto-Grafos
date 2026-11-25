import pytest
from src.graphs.algorithms import dijkstra
from src.graphs.graph import Grafo


def test_dijkstra_encontra_menor_custo():
    grafo = Grafo()
    for vertice in ("A", "B", "C"):
        grafo.adicionar_no(vertice)
    grafo.ligar("A", "C", 10)
    grafo.ligar("A", "B", 2)
    grafo.ligar("B", "C", 3)

    distancias, antecessores = dijkstra(grafo, "A")

    assert distancias["C"] == 5
    assert antecessores["C"] == "B"
    assert antecessores["B"] == "A"


def test_dijkstra_recusa_peso_negativo():
    grafo = Grafo()
    for vertice in ("A", "B", "D", "E"):
        grafo.adicionar_no(vertice)
    grafo.ligar("A", "B", 1)
    # O arco negativo fica fora do componente alcançável a partir de A.
    grafo.ligar("D", "E", -1)

    with pytest.raises(ValueError, match="peso negativo"):
        dijkstra(grafo, "A")
