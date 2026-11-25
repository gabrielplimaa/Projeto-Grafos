import pytest
from src.graphs.estados import construir_grafo_estados, rotulo


def test_mapa_minimo_contado_a_mao():
    # Mapa 4x6:
    # ######
    # #S.a.#
    # #>.A.#
    # ####G#
    mapa = [
        "######",
        "#S.a.#",
        "#>.A.#",
        "####G#",
    ]
    grafo, inicio = construir_grafo_estados(mapa)

    # Estados alcançáveis (excluindo o nó virtual ALVO):
    # Camada sem chaves (-):
    #   (1,1)|-|{} (S) -> vai para (1,2) e (2,1)
    #   (1,2)|-|{} (.) -> vai para (1,1) e (1,3) [pega chave a]
    #   (2,1)|-|{} (>) -> esteira para L (2,2)
    #   (2,2)|-|{} (.) -> vai para (1,2) e (2,1) [porta A (2,3) bloqueada]
    # Camada com chave a (a):
    #   (1,3)|a|{} (a) -> vai para (1,2)|a e (1,4)|a
    #   (1,2)|a|{} (.) -> vai para (1,1)|a, (1,3)|a, (2,2)|a
    #   (1,1)|a|{} (S) -> vai para (1,2)|a, (2,1)|a
    #   (2,1)|a|{} (>) -> esteira para L (2,2)|a
    #   (2,2)|a|{} (.) -> vai para (1,2)|a, (2,3)|a, (2,1)|a
    #   (1,4)|a|{} (.) -> vai para (2,4)|a, (1,3)|a
    #   (2,3)|a|{} (A) -> vai para (1,3)|a, (2,4)|a, (2,2)|a
    #   (2,4)|a|{} (.) -> vai para (1,4)|a, (3,4)|a, (2,3)|a
    #   (3,4)|a|{} (G) -> fim do jogo (só liga ao ALVO com custo 0)
    # Total = 13 estados reais + 1 ALVO = 14 vértices
    vertices_reais = [v for v in grafo.retornar_vertices() if v != "ALVO"]
    assert len(vertices_reais) == 13

    # Verifica mudança de camada ao coletar chave 'a'
    vizinhos_1_2 = [dest for dest, _ in grafo.retornar_vizinhos(((1, 2), frozenset(), frozenset()))]
    assert ((1, 3), frozenset({"a"}), frozenset()) in vizinhos_1_2


def test_esteira_para_parede_gera_beco():
    # Esteira '>' em (1,2) aponta para parede '#' em (1,3) -> grau de saída 0
    mapa = [
        "#####",
        "#S>.#",
        "#..G#",
        "#####",
    ]
    # Ajustando (1,3) para parede:
    mapa_beco = [
        "#####",
        "#S>#",
        "#.G#",
        "####",
    ]
    grafo, _ = construir_grafo_estados(mapa_beco)
    estado_esteira = ((1, 2), frozenset(), frozenset())
    assert grafo.retornar_vizinhos(estado_esteira) == []