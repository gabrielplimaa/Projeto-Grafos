class Grafo:
    def __init__(self):
        self.adjacencia = {}
        self.movimentos = {}  # Guarda {(origem, destino): 'N'|'L'|'S'|'O'}

    def adicionar_no(self, vertice):
        if vertice in self.adjacencia:
            raise ValueError(f"Vértice já existe: {vertice}")
        self.adjacencia[vertice] = []

    def ligar(self, origem, destino, peso, movimento=None):
        if origem not in self.adjacencia or destino not in self.adjacencia:
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