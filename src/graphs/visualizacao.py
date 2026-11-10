# visualizacao.py
import matplotlib.pyplot as plt
import networkx as nx

def desenhar_grafo(grafo):
    G = nx.DiGraph()

    # Adiciona nós e arestas com pesos
    for origem, conexoes in grafo.adjacencia.items():
        for destino, peso in conexoes:
            G.add_edge(origem, destino, weight=peso)

    # Layout automático para grafos não baseados em grid/mapa
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(8, 6))
    
    # Desenhar nós e arestas
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15, edge_color="gray")
    nx.draw_networkx_labels(G, pos, font_weight="bold")

    # Desenhar os pesos nas arestas
    pesos = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos)

    plt.title("Visualização do Grafo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()