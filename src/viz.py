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
            # #[IA] chat gpt 6.2 sol - usa a posicao tanto de um estado com bonus quanto de um no simples.
            if isinstance(no[0], tuple):
                i, j = no[0]
            else:
                i, j = no

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


# ======================= Figuras da Seção 8 do enunciado =======================
# [IA] Claude – sintaxe de matplotlib/networkx para desenhar as figuras da Seção 8.
# Estas funções só desenham: grafo, caminhos, antecessores e distâncias vêm do código
# do grupo (estados.py, algorithms.py, cli.py). As cores e destaques marcados como
# PROVISÓRIO são decisão do grupo e devem ser justificados no relatório.

from pathlib import Path

import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from src.labirinto_interativo import rotulo

# Cores do terreno: as do desenhar_grafo acima; "#", esteiras, "+" e "*" são PROVISÓRIAS.
CORES_TERRENO = {
    "#": "#2d3436", ".": "#ecf0f1", "S": "#2ecc71", "G": "#e74c3c",
    ",": "#95a5a6", "~": "#3498db",
    "a": "#f1c40f", "b": "#f1c40f", "c": "#f1c40f", "d": "#f1c40f",
    "A": "#e67e22", "B": "#e67e22", "C": "#e67e22", "D": "#e67e22",
    ">": "#dfe6e9", "<": "#dfe6e9", "^": "#dfe6e9", "v": "#dfe6e9",
    "+": "#a29bfe", "*": "#fd79a8",
}
NOMES_TERRENO = {
    "#": "parede", ".": "chão", "S": "início (S)", "G": "saída (G)", ",": "lama (custo 3)",
    "~": "água (custo 5)", "a": "chave", "b": "chave", "c": "chave", "d": "chave",
    "A": "porta", "B": "porta", "C": "porta", "D": "porta",
    ">": "esteira", "<": "esteira", "^": "esteira", "v": "esteira",
    "+": "bônus (+)", "*": "fonte (*)",
}
CORES_CAMADAS = ["#000000", "#555555", "#888888", "#aaaaaa", "#333333", "#777777"]  # PROVISÓRIO
COR_ARCO_CAMADA = "#b2bec3"          # arcos dentro da mesma camada (PROVISÓRIO)
COR_ARCO_ENTRE_CAMADAS = "#d35400"   # arcos que mudam de camada (PROVISÓRIO)
MAPA_DE_CORES_HEATMAP = "Greys"      # PROVISÓRIO
COR_PAREDE_HEATMAP = "#ffffff"       # PROVISÓRIO
DPI = 150


def _estados_reais(grafo):
    """Vértices do grafo sem o nó virtual ALVO, que não tem casa no mapa."""
    return [v for v in grafo.retornar_vertices() if v != "ALVO"]


def _partes(estado):
    """Aceita ((i, j), chaves) ou ((i, j), chaves, bonus)."""
    pos, chaves = estado[0], estado[1]
    bonus = estado[2] if len(estado) == 3 else frozenset()
    return pos, chaves, bonus


def _texto_chaves(chaves):
    return "".join(sorted(chaves)) or "-"


def _ordenar_camadas(camadas):
    """Ordena por número de chaves e depois alfabeticamente: -, a, b, ab, abc..."""
    return sorted(camadas, key=lambda c: (0 if c == "-" else len(c), c))


def _salvar(fig, saida):
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return saida


def _desenhar_grade(ax, mapa, escrever_simbolos):
    """Pinta a grade com uma cor por símbolo e devolve os símbolos presentes."""
    simbolos = sorted(set("".join(mapa)))
    indice = {s: k for k, s in enumerate(simbolos)}
    matriz = [[indice[s] for s in linha] for linha in mapa]
    cores = ListedColormap([CORES_TERRENO.get(s, "#ffffff") for s in simbolos])
    ax.imshow(matriz, cmap=cores, vmin=-0.5, vmax=len(simbolos) - 0.5, interpolation="nearest")
    if escrever_simbolos:
        for i, linha in enumerate(mapa):
            for j, s in enumerate(linha):
                if s not in "#.":
                    ax.text(j, i, s, ha="center", va="center", fontsize=8, color="#1f2933")
    ax.set_xlabel("coluna")
    ax.set_ylabel("linha")
    return simbolos


def _legenda_terreno(simbolos):
    """Um quadrado por tipo de casa presente no mapa (chaves juntas, portas juntas...)."""
    vistos, itens = set(), []
    for s in simbolos:
        nome = NOMES_TERRENO.get(s, s)
        if nome not in vistos:
            vistos.add(nome)
            itens.append(Patch(facecolor=CORES_TERRENO.get(s, "#ffffff"), edgecolor="#636e72", label=nome))
    return itens


def desenhar_percurso(mapa, caminho, saida, titulo):
    """Caminho sobre a grade, com a cor de cada trecho dada pela camada (chaves) do destino.

    caminho: lista de estados na ordem do percurso (vem de reconstruir_caminho do grupo).
    """
    linhas, colunas = len(mapa), len(mapa[0])
    pequeno = colunas <= 30
    fig, ax = plt.subplots(figsize=(max(6, colunas * 0.32), max(3, linhas * 0.32) + 1))
    simbolos = _desenhar_grade(ax, mapa, escrever_simbolos=pequeno)

    camadas = []
    for estado in caminho:
        c = _texto_chaves(_partes(estado)[1])
        if c not in camadas:
            camadas.append(c)
    cor_da_camada = {c: CORES_CAMADAS[k % len(CORES_CAMADAS)] for k, c in enumerate(camadas)}

    largura = 3 if pequeno else 2
    for anterior, atual in zip(caminho, caminho[1:]):
        (i0, j0), (i1, j1) = _partes(anterior)[0], _partes(atual)[0]
        cor = cor_da_camada[_texto_chaves(_partes(atual)[1])]
        ax.plot([j0, j1], [i0, i1], color=cor, linewidth=largura, solid_capstyle="round")

    (i_ini, j_ini), (i_fim, j_fim) = _partes(caminho[0])[0], _partes(caminho[-1])[0]
    ax.plot(j_ini, i_ini, marker="o", markersize=9, markerfacecolor="white", markeredgecolor="black")
    ax.plot(j_fim, i_fim, marker="X", markersize=10, markerfacecolor="white", markeredgecolor="black")

    itens = [Line2D([], [], color=cor_da_camada[c], linewidth=3, label=f"trecho na camada {c}") for c in camadas]
    itens += [Line2D([], [], marker="o", linestyle="", markerfacecolor="white", markeredgecolor="black", label="início do percurso"),
              Line2D([], [], marker="X", linestyle="", markerfacecolor="white", markeredgecolor="black", label="fim do percurso")]
    itens += _legenda_terreno(simbolos)
    ax.legend(handles=itens, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, title="Legenda", title_fontsize=9)
    ax.set_title(titulo)
    return _salvar(fig, saida)


def desenhar_camadas(grafo, mapa, saida, titulo):
    """Grafo de estados com uma faixa por camada (conjunto de chaves).

    Cada estado fica na posição da sua casa dentro da faixa da sua camada; arcos que
    mudam de camada são destacados.
    """
    linhas = len(mapa)
    estados = _estados_reais(grafo)
    camadas = _ordenar_camadas({_texto_chaves(_partes(e)[1]) for e in estados})
    faixa = {c: k for k, c in enumerate(camadas)}
    altura_faixa = linhas + 2

    # Estados da mesma casa e da mesma camada (bônus diferentes) ficam lado a lado.
    ocupacao, pos = {}, {}
    for e in estados:
        (i, j), chaves, _ = _partes(e)
        c = _texto_chaves(chaves)
        k = ocupacao.get((i, j, c), 0)
        ocupacao[(i, j, c)] = k + 1
        pos[e] = (j + 0.4 * k, -(i + faixa[c] * altura_faixa))

    G = nx.DiGraph()
    G.add_nodes_from(estados)
    dentro, entre = [], []
    for origem, destino, _peso in grafo.retornar_ligacoes():
        if origem == "ALVO" or destino == "ALVO":
            continue
        G.add_edge(origem, destino)
        mesma = _texto_chaves(_partes(origem)[1]) == _texto_chaves(_partes(destino)[1])
        (dentro if mesma else entre).append((origem, destino))

    largura = max(8, len(mapa[0]) * 0.5)
    fig, ax = plt.subplots(figsize=(largura, max(4, len(camadas) * (linhas + 2) * 0.45)))
    cores_nos = [CORES_TERRENO.get(mapa[_partes(e)[0][0]][_partes(e)[0][1]], "#ffffff") for e in estados]
    nx.draw_networkx_edges(G, pos, edgelist=dentro, ax=ax, edge_color=COR_ARCO_CAMADA, arrowstyle="->", arrowsize=8, width=1)
    nx.draw_networkx_edges(G, pos, edgelist=entre, ax=ax, edge_color=COR_ARCO_ENTRE_CAMADAS, arrowstyle="->", arrowsize=12, width=2.2)
    nx.draw_networkx_nodes(G, pos, nodelist=estados, ax=ax, node_color=cores_nos, node_size=110, edgecolors="black", linewidths=0.6)
    simbolos_nos = {e: mapa[_partes(e)[0][0]][_partes(e)[0][1]] for e in estados}
    nx.draw_networkx_labels(G, pos, labels={e: s for e, s in simbolos_nos.items() if s != "."}, ax=ax, font_size=6)

    for c, k in faixa.items():
        ax.text(-1.5, -(k * altura_faixa + (linhas - 1) / 2), f"camada {c}", ha="right", va="center", fontsize=10, fontweight="bold")
        if k > 0:
            ax.axhline(-(k * altura_faixa - 1.5), color="#dfe6e9", linewidth=1)

    itens = [Line2D([], [], color=COR_ARCO_CAMADA, linewidth=1, label=f"arco dentro da camada ({len(dentro)})"),
             Line2D([], [], color=COR_ARCO_ENTRE_CAMADAS, linewidth=2.2, label=f"arco que muda de camada ({len(entre)})")]
    itens += _legenda_terreno(sorted(set(simbolos_nos.values())))
    ax.legend(handles=itens, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, title="Legenda", title_fontsize=9)
    ax.set_title(titulo)
    ax.set_xlim(-6, len(mapa[0]) + 1)
    ax.axis("off")
    return _salvar(fig, saida)


def desenhar_arvore_bfs(grafo, mapa, distancias, antecessores, saida, titulo):
    """Árvore BFS: arcos (antecessor, estado) da BFS do grupo, um nível por linha.

    distancias e antecessores vêm da bfs() do grupo; o nível de um estado é a sua distância.
    """
    # O ALVO fica fora do desenho: ele não tem casa no mapa (é só o fim de todo caminho).
    alcancados = [e for e in _estados_reais(grafo) if distancias[e] != float("inf")]
    niveis = {}
    for e in alcancados:
        niveis.setdefault(distancias[e], []).append(e)

    pos = {}
    for nivel, estados in niveis.items():
        estados.sort(key=lambda e: rotulo(e, mapa))
        for k, e in enumerate(estados):
            pos[e] = (k - (len(estados) - 1) / 2, -nivel)

    T = nx.DiGraph()
    T.add_nodes_from(alcancados)
    T.add_edges_from((antecessores[e], e) for e in alcancados if antecessores[e] is not None)

    largura_max = max(len(v) for v in niveis.values())
    altura = len(niveis)
    fig, ax = plt.subplots(figsize=(max(7, largura_max * 2.6), max(4, altura * 0.42)))
    cores_nos = [CORES_TERRENO.get(mapa[_partes(e)[0][0]][_partes(e)[0][1]], "#ffffff") for e in alcancados]
    nx.draw_networkx_edges(T, pos, ax=ax, edge_color="#636e72", arrowstyle="->", arrowsize=8, width=1)
    nx.draw_networkx_nodes(T, pos, nodelist=alcancados, ax=ax, node_color=cores_nos, node_size=110, edgecolors="black", linewidths=0.6)
    for e in alcancados:
        x, y = pos[e]
        ax.text(x + 0.12, y, rotulo(e, mapa), fontsize=6.5, va="center", ha="left")

    ax.set_yticks([-n for n in sorted(niveis)])
    ax.set_yticklabels([str(n) for n in sorted(niveis)], fontsize=7)
    ax.set_ylabel("nível da BFS (distância em passos)")
    ax.set_xticks([])
    ax.tick_params(left=True, labelleft=True)
    for lado in ("top", "right", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.set_xlim(-largura_max / 2 - 0.5, largura_max / 2 + 1.5)

    simbolos = sorted({mapa[_partes(e)[0][0]][_partes(e)[0][1]] for e in alcancados})
    itens = [Line2D([], [], color="#636e72", label="arco da árvore BFS (antecessor → estado)")] + _legenda_terreno(simbolos)
    ax.legend(handles=itens, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, title="Legenda (cor = casa do estado)", title_fontsize=9)
    ax.set_title(titulo)
    return _salvar(fig, saida)


def desenhar_heatmap_multiplicidade(grafo, mapa, saida, titulo):
    """Número de estados do grafo de estados em cada casa do mapa (multiplicidade)."""
    linhas, colunas = len(mapa), len(mapa[0])
    contagem = np.zeros((linhas, colunas))
    for e in _estados_reais(grafo):
        i, j = _partes(e)[0]
        contagem[i, j] += 1
    paredes = np.array([[s == "#" for s in linha] for linha in mapa])
    dados = np.ma.masked_array(contagem, mask=paredes)

    # A escala começa num cinza claro (0.15) para a casa com 0 estados não se confundir
    # com a parede, que fica branca.
    cores = ListedColormap(plt.get_cmap(MAPA_DE_CORES_HEATMAP)(np.linspace(0.15, 1, 256)))
    cores.set_bad(COR_PAREDE_HEATMAP)
    fig, ax = plt.subplots(figsize=(max(6, colunas * 0.3), max(3, linhas * 0.3) + 1))
    imagem = ax.imshow(dados, cmap=cores, interpolation="nearest", vmin=0)
    maximo = int(contagem.max())
    barra = fig.colorbar(imagem, ax=ax, fraction=0.025, pad=0.02, ticks=range(0, maximo + 1, max(1, maximo // 8)))
    barra.set_label("multiplicidade (nº de estados na casa)")

    if colunas <= 40:
        for i in range(linhas):
            for j in range(colunas):
                if not paredes[i, j]:
                    cor = "white" if contagem[i, j] > maximo / 2 else "#1f2933"
                    ax.text(j, i, int(contagem[i, j]), ha="center", va="center", fontsize=7, color=cor)

    ax.legend(handles=[Patch(facecolor=COR_PAREDE_HEATMAP, edgecolor="#636e72", label="parede")], loc="upper left",
              bbox_to_anchor=(1.12, 1), fontsize=8)
    ax.set_xlabel("coluna")
    ax.set_ylabel("linha")
    ax.set_title(titulo)
    return _salvar(fig, saida)
