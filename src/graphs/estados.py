from .io import ler_mapa
from .graph import Grafo

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

mapa = ler_mapa("data\mapas\m01_terreno.txt")
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


print(grafo.adjacencia)
            


