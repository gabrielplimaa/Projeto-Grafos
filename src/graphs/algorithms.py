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


#IA[CHAT GPT] 
def dfs(grafo: Grafo, vertice_origem):
    vertices = grafo.retornar_vertices()

    if vertice_origem not in vertices:
        print("Erro: vértice de origem não existe no grafo")
        return

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