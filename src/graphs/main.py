from graph import Grafo
from algorithms import dijkstra
from visualizacao import desenhar_grafo

g = Grafo()

# Adiciona os vértices. Z fica isolado.
for no in ("A", "B", "C", "D", "E", "F", "Z"):
    g.adicionar_no(no)

# Adiciona os arcos na ordem em que a DFS deve examiná-los.
g.ligar("A", "B", 10)
g.ligar("A", "C", 2)
g.ligar("C", "B", 3)
g.ligar("B", "D", 2)
g.ligar("C", "D", 9)
g.ligar("D", "E", 4)
g.ligar("B", "E", 8)
g.ligar("E", "F", 1)

desenhar_grafo(g)
