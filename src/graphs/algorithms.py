#BFS, DFS, Dijkstra e Bellman-Ford

from collections import deque
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

        for destino, peso in grafo.retornar_vizinhos(vertice_atual):
            if peso < 0:
                raise ValueError(f"Dijkstra não aceita arestas com peso negativo (peso {peso})")
            nova_distancia = distancias[vertice_atual] + peso
            if nova_distancia < distancias[destino]:
                distancias[destino] = nova_distancia
                antecessores[destino] = vertice_atual

    return distancias, antecessores


#IA[Claude]
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


#IA[CHAT GPT] 
def dfs(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    contagens = {"arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0}
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
            contagens["arvore"] += 1
            descoberta[destino] = len(descoberta)  # Registra a ordem da descoberta.
            em_exploracao.add(destino)             # Abre a exploração desse vértice.
            pilha.append((destino, 0))             # Começa pela primeira saída dele.

        elif destino in em_exploracao:
            # Retorno: a seta aponta para um vértice que ainda está na pilha.
            contagens["retorno"] += 1

        elif descoberta[destino] > descoberta[vertice_atual]:
            # Avanço: o destino já terminou e foi descoberto dentro do meu ramo.
            contagens["avanco"] += 1

        else:
            # Cruzamento: o destino já terminou em outro ramo, explorado antes.
            contagens["cruzamento"] += 1
    return contagens


def bellman_ford(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()
    
    if vertice_origem not in vertices:
        raise ValueError(f"Vértice de origem não existe no grafo: {vertice_origem}")

    distancias = {v: float('inf') for v in vertices}
    distancias[vertice_origem] = 0
    antecessores = {v: None for v in vertices}

    for v in range(len(vertices)-1):
        for vertice_atual in vertices:

            for destino, peso in grafo.retornar_vizinhos(vertice_atual):
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[destino]:
                    distancias[destino] = nova_distancia
                    antecessores[destino] = vertice_atual

    for vertice_atual in vertices:
        for destino, peso in grafo.retornar_vizinhos(vertice_atual):
            nova_distancia = distancias[vertice_atual] + peso

            if nova_distancia < distancias[destino]:    
                raise ValueError("O grafo contém um ciclo de peso negativo")

    return distancias, antecessores