# BFS, DFS, Dijkstra e Bellman-Ford

from collections import deque
import heapq
from src.graphs.graph import Grafo


def dijkstra(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    # Verifica TODOS os arcos do grafo antes de iniciar a busca
    for u in vertices:
        for destino, peso in grafo.retornar_vizinhos(u):
            if peso < 0:
                raise ValueError(f"Dijkstra não aceita arestas com peso negativo (peso {peso})")

    distancias = {v: float('inf') for v in vertices}
    distancias[vertice_origem] = 0
    antecessores = {v: None for v in vertices}
    visitados = set()
    contador = 0
    heap = [(0, contador, vertice_origem)]

    while heap:
        dist_atual, _, vertice_atual = heapq.heappop(heap)

        if vertice_atual in visitados:
            continue
        visitados.add(vertice_atual)

        for destino, peso in grafo.retornar_vizinhos(vertice_atual):
            if peso < 0:
                raise ValueError(f"Dijkstra não aceita arestas com peso negativo (peso {peso})")
            nova_distancia = dist_atual + peso
            if nova_distancia < distancias[destino]:
                distancias[destino] = nova_distancia
                antecessores[destino] = vertice_atual
                contador += 1
                heapq.heappush(heap, (nova_distancia, contador, destino))

    return distancias, antecessores


# [IA] Claude – Apoio na estruturação inicial da busca em largura (BFS)
def bfs(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    distancias = {v: float('inf') for v in vertices}
    distancias[vertice_origem] = 0
    antecessores = {v: None for v in vertices}
    fila = deque([vertice_origem])

    while fila:
        vertice_atual = fila.popleft()

        for destino, _ in grafo.retornar_vizinhos(vertice_atual):
            if distancias[destino] == float('inf'):
                distancias[destino] = distancias[vertice_atual] + 1
                antecessores[destino] = vertice_atual
                fila.append(destino)

    return distancias, antecessores


# [IA] ChatGPT – Apoio na lógica iterativa de classificação de arcos na DFS
def dfs(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    contagens = {"arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0}
    arcos_classificados = []
    descoberta = {vertice_origem: 0}
    em_exploracao = {vertice_origem}
    pilha = [(vertice_origem, 0)]

    while pilha:
        # Lê o topo da pilha sem retirar o vértice.
        vertice_atual, indice = pilha[-1]
        vizinhos = grafo.retornar_vizinhos(vertice_atual)

        if indice == len(vizinhos):
            em_exploracao.remove(vertice_atual)
            pilha.pop()
            continue

        destino, _peso = vizinhos[indice]
        # Guarda onde retomar quando este vértice voltar ao topo.
        pilha[-1] = (vertice_atual, indice + 1)

        if destino not in descoberta:
            # Árvore: foi por esta seta que encontrei o destino pela primeira vez.
            tipo = "arvore"
            descoberta[destino] = len(descoberta)
            em_exploracao.add(destino)
            pilha.append((destino, 0))

        elif destino in em_exploracao:
            # Retorno: a seta aponta para um vértice que ainda está na pilha.
            tipo = "retorno"

        elif descoberta[destino] > descoberta[vertice_atual]:
            # Avanço: o destino já terminou e foi descoberto dentro do meu ramo.
            tipo = "avanco"

        else:
            # Cruzamento: o destino já terminou em outro ramo, explorado antes.
            tipo = "cruzamento"

        contagens[tipo] += 1
        arcos_classificados.append((vertice_atual, destino, tipo))

    return {
        "contagens": contagens,
        "arcos": arcos_classificados,
        "tem_ciclo": contagens["retorno"] > 0,
    }


def bellman_ford(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    distancias = {v: float('inf') for v in vertices}
    distancias[vertice_origem] = 0
    antecessores = {v: None for v in vertices}

    for _ in range(len(vertices) - 1):
        relaxou = False
        for vertice_atual in vertices:
            if distancias[vertice_atual] == float('inf'):
                continue

            for destino, peso in grafo.retornar_vizinhos(vertice_atual):
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[destino]:
                    distancias[destino] = nova_distancia
                    antecessores[destino] = vertice_atual
                    relaxou = True

        if not relaxou:
            break

    for vertice_atual in vertices:
        if distancias[vertice_atual] == float('inf'):
            continue

        for destino, peso in grafo.retornar_vizinhos(vertice_atual):
            nova_distancia = distancias[vertice_atual] + peso

            if nova_distancia < distancias[destino]:
                antecessores[destino] = vertice_atual
                x = destino

                for _ in range(len(vertices)):
                    x = antecessores[x]

                ciclo = [x]
                atual = antecessores[x]
                while atual != x:
                    ciclo.append(atual)
                    atual = antecessores[atual]
                ciclo.append(x)
                ciclo.reverse()

                custo_ciclo = 0
                for i in range(len(ciclo) - 1):
                    u = ciclo[i]
                    v = ciclo[i + 1]
                    menor_peso = float('inf')
                    for d, p in grafo.retornar_vizinhos(u):
                        if d == v and p < menor_peso:
                            menor_peso = p
                    custo_ciclo += menor_peso

                return {
                    "tem_ciclo_negativo": True,
                    "distancias": distancias,
                    "antecessores": antecessores,
                    "ciclo": ciclo,
                    "custo_ciclo": custo_ciclo,
                }

    return {
        "tem_ciclo_negativo": False,
        "distancias": distancias,
        "antecessores": antecessores,
        "ciclo": None,
        "custo_ciclo": None,
    }