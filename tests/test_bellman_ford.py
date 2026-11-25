from src.graphs.algorithms import bellman_ford
from src.graphs.graph import Grafo


def test_bellman_ford_peso_negativo_sem_ciclo():
    # A -> B (4), A -> C (5), C -> B (-3), B -> D (2)
    # Menor custo A -> D = A -> C -> B -> D = 5 - 3 + 2 = 4
    grafo = Grafo()
    for v in ["A", "B", "C", "D"]:
        grafo.adicionar_no(v)
    grafo.ligar("A", "B", 4)
    grafo.ligar("A", "C", 5)
    grafo.ligar("C", "B", -3)
    grafo.ligar("B", "D", 2)

    res = bellman_ford(grafo, "A")
    assert res["tem_ciclo_negativo"] is False
    assert res["distancias"]["D"] == 4
    assert res["ciclo"] is None


def test_bellman_ford_detecta_ciclo_negativo():
    # A -> B (1), B -> C (-2), C -> B (-1) => ciclo B -> C -> B de custo -3
    grafo = Grafo()
    for v in ["A", "B", "C"]:
        grafo.adicionar_no(v)
    grafo.ligar("A", "B", 1)
    grafo.ligar("B", "C", -2)
    grafo.ligar("C", "B", -1)

    res = bellman_ford(grafo, "A")
    assert res["tem_ciclo_negativo"] is True
    assert res["custo_ciclo"] == -3
    assert res["ciclo"] is not None
    assert res["ciclo"][0] == res["ciclo"][-1]