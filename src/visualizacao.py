import matplotlib.pyplot as plt
import networkx as nx

def desenhar_grafo(grafo, mapa=None):
    # Se por acaso for passada uma tupla, extrai a primeira posição (o objeto Grafo)
    if isinstance(grafo, tuple):
        grafo = grafo[0]

    G = nx.DiGraph()

    # 1. Adicionar nós e arestas com pesos
    for origem, conexoes in grafo.adjacencia.items():
        for destino, peso in conexoes:
            G.add_edge(origem, destino, weight=peso)

    plt.figure(figsize=(10, 8))

    primeiro_no = next(iter(G.nodes()), None)

    # 2. SE FOR LABIRINTO (Coordenadas de grelha 2D)
    if mapa is not None and isinstance(primeiro_no, tuple):
        pos = {}
        cores_nos = []
        labels_nos = {}

        for no in G.nodes():
            # Trata nós do tipo ((i, j), chaves) ou apenas (i, j)
            if isinstance(no[0], tuple):
                (i, j), chaves = no
            else:
                i, j = no
                chaves = None

            # Mapeamento de coordenadas (x=coluna, y=-linha) para alinhar a imagem
            pos[no] = (j, -i)
            simbolo = mapa[i][j]
            labels_nos[no] = simbolo

            if simbolo == "S":
                cores_nos.append("#2ecc71")    # Verde (Início)
            elif simbolo == "G":
                cores_nos.append("#e74c3c")  # Vermelho (Objetivo)
            elif simbolo in "abcd":
                cores_nos.append("#f1c40f")  # Amarelo (Chaves)
            elif simbolo in "ABCD":
                cores_nos.append("#e67e22")  # Laranja (Portas)
            elif simbolo == "~":
                cores_nos.append("#3498db")  # Azul (Água)
            elif simbolo == ",":
                cores_nos.append("#95a5a6")  # Cinza (Grama)
            else:
                cores_nos.append("#ecf0f1")  # Cinza claro (Caminho)

        nx.draw_networkx_nodes(G, pos, node_color=cores_nos, node_size=300, edgecolors="black")
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=8, edge_color="#bdc3c7")
        nx.draw_networkx_labels(G, pos, labels=labels_nos, font_size=8, font_weight="bold")

    # 3. SE FOR GRAFO ABSTRATO ("A", "B", "C"...)
    else:
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15, edge_color="gray")
        nx.draw_networkx_labels(G, pos, font_weight="bold")
        pesos = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos)

    plt.title("Visualização Estruturada do Labirinto / Grafo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()