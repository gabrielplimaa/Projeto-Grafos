from .io import ler_mapa
from .graph import Grafo
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
    "+": -4,
}

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
DESLOCAMENTOS = [
    (-1, 0, "N"),
    (0, 1, "L"),
    (1, 0, "S"),
    (0, -1, "O"),
]


def construir_grafo_estados(mapa, fonte_consumivel=False):
    grafo = Grafo()
    posicao_inicial = encontrar_inicio(mapa)
    inicio = (posicao_inicial, frozenset(), frozenset())
    grafo.adicionar_no(inicio)
    grafo.adicionar_no("ALVO")

    # [IA] Claude – correção de sintaxe: deque([...]) em vez de deque[...]
    fila = deque([inicio])
    visitados = {inicio}

    while fila:
        atual = fila.popleft()
        (i, j), chaves, consumidos = atual

        if mapa[i][j] == "G":
            grafo.ligar(atual, "ALVO", 0)
            continue

        origem = mapa[i][j]
        for di, dj, mov in DESLOCAMENTOS:
            if origem in direcoes_esteiras and (di, dj) != direcoes_esteiras[origem]:
                continue

            novo_i = i + di
            novo_j = j + dj
            if novo_i < 0 or novo_i >= len(mapa) or novo_j < 0 or novo_j >= len(mapa[novo_i]):
                continue

            simbolo = mapa[novo_i][novo_j]
            # [IA] Claude – usa a variável simbolo em vez de reler o mapa
            if simbolo == "#":
                continue
            if simbolo in "ABCD" and simbolo.lower() not in chaves:
                continue

            novo_chaves = chaves | {simbolo} if simbolo in "abcd" else chaves
            posicao = (novo_i, novo_j)
            novos_consumidos = consumidos
            custo = custos[simbolo]

            if simbolo == "+":
                if posicao in consumidos:
                    custo = custos["."]
                else:
                    novos_consumidos = consumidos | {posicao}
            elif simbolo == "*" and fonte_consumivel:
                if posicao in consumidos:
                    custo = custos["."]
                else:
                    novos_consumidos = consumidos | {posicao}

            novo = (posicao, novo_chaves, novos_consumidos)
            if novo not in visitados:
                grafo.adicionar_no(novo)
                visitados.add(novo)
                fila.append(novo)

            grafo.ligar(atual, novo, custo, movimento=mov)

    return grafo, inicio


def construir_grafo_posicoes(mapa, porta_como_parede=False):
    grafo = Grafo()
    bloqueios = {"#"}
    if porta_como_parede:
        bloqueios.update({"A", "B", "C", "D"})

    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] not in bloqueios:
                grafo.adicionar_no((i, j))

    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            origem = mapa[i][j]
            if origem in bloqueios or origem == "G":
                continue

            for di, dj, mov in DESLOCAMENTOS:
                if origem in direcoes_esteiras and (di, dj) != direcoes_esteiras[origem]:
                    continue

                ni, nj = i + di, j + dj
                if 0 <= ni < len(mapa) and 0 <= nj < len(mapa[ni]):
                    simbolo = mapa[ni][nj]
                    if simbolo not in bloqueios and simbolo in custos:
                        grafo.ligar((i, j), (ni, nj), custos[simbolo], movimento=mov)

    return grafo

if __name__ == "__main__":
    # [IA] Claude – correção do caminho (barras normais, funciona em qualquer sistema)
    mapa = ler_mapa("data/mapas/m02_uma_chave.txt")

    #[IA] ChatGPT – print temporário de teste (exibição dos grafos construídos)
    #grafo_posicoes = construir_grafo_posicoes(mapa)
    #grafo_estados, inicio = construir_grafo_estados(mapa)

    # print("\nGRAFO DE POSIÇÕES")
    # for vertice, vizinhos in grafo_posicoes.adjacencia.items():
    #     print(vertice, "->", vizinhos)

    # print("\nGRAFO DE ESTADOS")
    # for vertice, vizinhos in grafo_estados.adjacencia.items():
    #     print(vertice, "->", vizinhos)



