from .io import ler_mapa  # Funciona diretamente se não houver 'from .io'
from .graph import Grafo
from .visualizacao import desenhar_grafo

# 1. Instanciar o grafo e carregar o mapa
grafo_posicoes = Grafo()

# Certifique-se de que o caminho aponta corretamente para a pasta data
mapa = ler_mapa("data/mapas/m02_uma_chave.txt")

# 2. Tabela de custos de movimento
custos = {
    ".": 1, "S": 1, "G": 1, ",": 3, "~": 5,
    "a": 1, "b": 1, "c": 1, "d": 1,
    "A": 1, "B": 1, "C": 1, "D": 1,
    ">": 1, "<": 1, "^": 1, "v": 1, "*": -2
}

# 3. Adicionar as posições livres (diferentes de '#') como nós
for i in range(len(mapa)):
    for j in range(len(mapa[i])):
        if mapa[i][j] != "#":
            grafo_posicoes.adicionar_no((i, j))

# 4. Criar as conexões direcionadas e validadas por direção/peso
for i in range(len(mapa)):
    for j in range(len(mapa[i])):
        if mapa[i][j] != "#" and mapa[i][j] != "G":
            origem = mapa[i][j]
            
            # Cima
            if i > 0 and (origem not in "<>^v" or origem == "^"):
                simbolo = mapa[i-1][j]
                if simbolo in custos:
                    grafo_posicoes.ligar((i, j), (i-1, j), custos[simbolo])

            # Direita
            if j < len(mapa[i]) - 1 and (origem not in "<>^v" or origem == ">"):
                simbolo = mapa[i][j+1]
                if simbolo in custos:
                    grafo_posicoes.ligar((i, j), (i, j+1), custos[simbolo])

            # Baixo
            if i < len(mapa) - 1 and (origem not in "<>^v" or origem == "v"):
                simbolo = mapa[i+1][j]
                if simbolo in custos:
                    grafo_posicoes.ligar((i, j), (i+1, j), custos[simbolo])

            # Esquerda
            if j > 0 and (origem not in "<>^v" or origem == "<"):
                simbolo = mapa[i][j-1]
                if simbolo in custos:
                    grafo_posicoes.ligar((i, j), (i, j-1), custos[simbolo])

# 5. Renderizar o labirinto
desenhar_grafo(grafo_posicoes, mapa)