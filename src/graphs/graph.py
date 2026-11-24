import random
import numpy as np
import pandas as pd

class Grafo:
    def __init__(self):
        self.adjacencia = {}
        self.movimentos = {}  # Guarda {(origem, destino): 'N'|'L'|'S'|'O'}

    def adicionar_no(self, vertice):
        if vertice in self.adjacencia:
            raise ValueError(f"Vértice já existe: {vertice}")
        self.adjacencia[vertice] = []

    def ligar(self, origem, destino, peso, movimento=None, criar_nos=False):
        if criar_nos:
            if origem not in self.adjacencia:
                self.adicionar_no(origem)
            if destino not in self.adjacencia:
                self.adicionar_no(destino)
        elif origem not in self.adjacencia or destino not in self.adjacencia:
            raise ValueError(f"Não existe um dos vértices no grafo: {origem}, {destino}")

        self.adjacencia[origem].append([destino, peso])
        if movimento is not None:
            self.movimentos[(origem, destino)] = movimento

    def retornar_vizinhos(self, vertice):
        if vertice not in self.adjacencia:
            raise ValueError(f"Vértice não existe no grafo: {vertice}")
        return self.adjacencia[vertice]

    def retornar_vertices(self):
        return list(self.adjacencia.keys())

    def retornar_ligacoes(self):
        lista_ligacoes = []
        for vertice in self.adjacencia:
            for adjacencias in self.adjacencia[vertice]:
                lista_ligacoes.append((vertice, adjacencias[0], adjacencias[1]))
        return lista_ligacoes

    def retornar_movimento(self, origem, destino):
        return self.movimentos.get((origem, destino), "")

    def grau_saida(self, vertice):
        if vertice not in self.adjacencia:
            raise ValueError(f"Vértice não existe no grafo: {vertice}")
        return len(self.adjacencia[vertice])

    def grau_entrada(self, vertice):
        if vertice not in self.adjacencia:
            raise ValueError(f"Vértice não existe no grafo: {vertice}")
        total = 0
        for origem in self.adjacencia:
            for destino, _ in self.adjacencia[origem]:
                if destino == vertice:
                    total += 1
        return total

    def graus_entrada_todos(self):
        """Calcula o grau de entrada de todos os nós em uma única passada O(V + E)."""
        graus = {v: 0 for v in self.adjacencia}
        for origem in self.adjacencia:
            for destino, _ in self.adjacencia[origem]:
                graus[destino] += 1
        return graus

    def transposto(self):
        """Cria um novo Grafo com todas as arestas invertidas (para buscar armadilhas a partir de ALVO)."""
        gt = Grafo()
        for vertice in self.adjacencia:
            gt.adicionar_no(vertice)

        for origem in self.adjacencia:
            for destino, peso in self.adjacencia[origem]:
                mov = self.movimentos.get((origem, destino))
                gt.ligar(destino, origem, peso, movimento=mov)
        return gt

def gerar_subgrafo_amostra(df: pd.DataFrame, fracao: float, seed: int = 42) -> pd.DataFrame:
    if not (0 < fracao <= 1.0):
        raise ValueError(f"A fração deve estar no intervalo (0, 1.0]. Recebido: {fracao}")

    if fracao == 1.0:
        return df.copy()

    nos_unicos = sorted(set(df["source"]).union(set(df["target"])))
    qtd_nos = max(1, int(len(nos_unicos) * fracao))

    rng = np.random.default_rng(seed)
    nos_selecionados = set(rng.choice(nos_unicos, size=qtd_nos, replace=False))

    condicao_origem = df["source"].isin(nos_selecionados)
    condicao_destino = df["target"].isin(nos_selecionados)

    return df[condicao_origem & condicao_destino].reset_index(drop=True)


def construir_grafo_de_dataframe(df: pd.DataFrame) -> Grafo:
    grafo = Grafo()

    for origem, destino, peso in zip(df["source"], df["target"], df["peso"]):
        grafo.ligar(origem, destino, float(peso), criar_nos=True)

    return grafo
    