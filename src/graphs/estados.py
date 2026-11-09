from .io import ler_mapa
from .graph import Grafo
from .algorithms import dijkstra
from collections import deque

custos = {
    ".": 1,
    "S": 1,
    "G": 1,
    ",": 3,
    "~": 5,
    "a": 1,
    "b": 1,
    "c": 1,
    "d": 1,
    "A": 1,
    "B": 1,
    "C": 1,
    "D": 1,
    ">": 1,
    "<": 1,
    "^": 1,
    "v": 1,
    "*": -2,
}

# [IA] Claude – correção do caminho (barras normais, funciona em qualquer sistema)
mapa = ler_mapa("data/mapas/m02_uma_chave.txt")

def encontrar_inicio(mapa):
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] == "S":
                return (i, j)


direcoes_esteiras = {
    "^": (-1, 0),
    ">": (0, 1),
    "v": (1, 0),
    "<": (0, -1),
}

def construir_grafo_estados(mapa):
    grafo = Grafo()
    posicao_inicial = encontrar_inicio(mapa)
    inicio = (posicao_inicial, frozenset())
    grafo.adicionar_no(inicio)
    # [IA] Claude – correção de sintaxe: deque([...]) em vez de deque[...]
    fila = deque([inicio])
    distancia = {inicio: 0}
    pai = {inicio: None}
    deslocamentos = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    while fila:
        (i, j), chaves = fila.popleft()
        atual = (i, j), chaves
        if mapa[i][j] == "G":
            continue
        for di, dj in deslocamentos:
            origem = mapa[i][j]
            if origem in direcoes_esteiras:
                if (di, dj) != direcoes_esteiras[origem]:
                    continue
            novo_i = i + di
            novo_j = j + dj
            if novo_i < 0 or novo_i >= len(mapa) or novo_j < 0 or novo_j >= len(mapa[i]):
                continue
            simbolo = mapa[novo_i][novo_j]
            # [IA] Claude – usa a variável simbolo em vez de reler o mapa
            if simbolo == "#":
                continue
            if simbolo in "ABCD" and simbolo.lower() not in chaves:
                continue
            novo_chaves = chaves
            if simbolo in "abcd":
                novo_chaves = chaves | {simbolo}
            novo = (novo_i, novo_j), novo_chaves
            if novo not in distancia:
                grafo.adicionar_no(novo)
                distancia[novo] = distancia[atual] + 1
                pai[novo] = atual
                fila.append(novo)
                print(distancia[novo], novo)
            grafo.ligar(atual, novo, custos[simbolo])  # [IA] Claude – print temporário de teste (distância e estado alcançado)
    return grafo, inicio

# [IA] Claude – print temporário de teste (número de estados alcançáveis)
def construir_grafo_posicoes(mapa):
    grafo = Grafo()
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] != "#":
                grafo.adicionar_no((i,j))

    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] != "#":
                if mapa[i][j] == "G":
                    continue

                origem = mapa[i][j]
                #verica se pode ir pra cima e se sim, faz a ligação
                if i > 0:   
                    if origem not in "<>^v" or origem == "^":
                        simbolo = mapa[i-1][j]
                        if simbolo in custos:
                            grafo.ligar((i, j), (i-1, j), custos[simbolo])

                #verifica se pode ir pra direita e se sim, faz a ligação
                if j < len(mapa[i]) - 1:
                    if origem not in "<>^v" or origem == ">":
                        simbolo = mapa[i][j+1]
                        if simbolo in custos:
                            grafo.ligar((i, j), (i, j+1), custos[simbolo])

                #verifica se pode ir pra baixo e se sim, faz a ligação
                if 	i < len(mapa) - 1:
                    if origem not in "<>^v" or origem == "v":
                        simbolo = mapa[i+1][j]
                        if simbolo in custos:
                            grafo.ligar((i, j), (i+1, j), custos[simbolo])

                #verifica se pode ir pra esquerda e se sim, faz a ligação
                if j > 0:
                    if origem not in "<>^v" or origem == "<":
                        simbolo = mapa[i][j-1]
                        if simbolo in custos:
                            grafo.ligar((i, j), (i, j-1), custos[simbolo])
    return grafo

#[IA] ChatGPT – print temporário de teste (exibição dos grafos construídos)
grafo_posicoes = construir_grafo_posicoes(mapa)
grafo_estados, inicio = construir_grafo_estados(mapa)

print("\nGRAFO DE POSIÇÕES")
for vertice, vizinhos in grafo_posicoes.adjacencia.items():
    print(vertice, "->", vizinhos)

print("\nGRAFO DE ESTADOS")
for vertice, vizinhos in grafo_estados.adjacencia.items():
    print(vertice, "->", vizinhos)



