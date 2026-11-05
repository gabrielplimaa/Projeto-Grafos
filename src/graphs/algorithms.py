#BFS, DFS, Dijkstra e Bellman-Ford

from .graph import Grafo

def dijkstra(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()
    
    if vertice_origem not in vertices:
        print("Erro: vértice de origem não existe no grafo")
        return

    distancias = {v: float('inf') for v in vertices}
    distancias[vertice_origem] = 0
    antecessores = {v: None for v in vertices}
    nao_visitados = list(vertices)

    while nao_visitados:
        vertice_atual = None
        menor_distancia = float('inf')

        for v in nao_visitados:
            if distancias[v] < menor_distancia:
                menor_distancia = distancias[v]
                vertice_atual = v

        if vertice_atual is None or menor_distancia == float('inf'):
            break

        nao_visitados.remove(vertice_atual)

        vizinhos = grafo.retornar_vizinhos(vertice_atual)
        if vizinhos:
            for destino, peso in vizinhos:
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[destino]:
                    distancias[destino] = nova_distancia
                    antecessores[destino] = vertice_atual

    return distancias, antecessores