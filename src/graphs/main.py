from graph import Grafo
from algorithms import dijkstra

g = Grafo()

# 1. Adicionar os vértices
nos = ["A", "B", "C", "D", "E", "F", "Z"]
for no in nos:
    g.adicionar_no(no)

# 2. Criar as conexões (com pesos diferentes)
# Caminho direto A -> B tem peso alto (10)
g.ligar("A", "B", 10)

# Atalho mais barato para chegar em B: A -> C (2) -> B (3) = Custo 5
g.ligar("A", "C", 2)
g.ligar("C", "B", 3)

# Continuação a partir de B e C
g.ligar("B", "D", 2)
g.ligar("C", "D", 9)
g.ligar("D", "E", 4)
g.ligar("B", "E", 8)
g.ligar("E", "F", 1)

# Obs: O nó "Z" ficou intencionalmente sem ligações (inalcançável)

# 3. Executar o Dijkstra a partir de "A"
distancia, anterior = dijkstra(g, "A")

print("--- RESULTADOS A PARTIR DE 'A' ---")
print("Distâncias:", distancia)
print("Antecessores:", anterior)