class Grafo:
    def __init__(self):
        self.adjacencia = {

        }

    def adicionar_no(self, vertice):
        if vertice in self.adjacencia:
            raise ValueError(f"Vértice já existe: {vertice}")
        self.adjacencia[vertice] = []

    def ligar(self, origem, destino, peso):
        if origem not in self.adjacencia or destino not in self.adjacencia:
            raise ValueError(f"Não existe um dos vértices no grafo: {origem}, {destino}")

        self.adjacencia[origem].append([destino, peso])

    def retornar_vizinhos(self, vertice):
        if vertice not in self.adjacencia:
            raise ValueError(f"Vértice não existe no grafo: {vertice}")
        return self.adjacencia[vertice]

    def retornar_vertices(self):
        lista_vertices = []
        for vertice in self.adjacencia:
            lista_vertices.append(vertice)

        return lista_vertices

    def retornar_ligacoes(self):
        lista_ligacoes = []

        for vertice in self.adjacencia:
            for adjacencias in self.adjacencia[vertice]:
                lista_ligacoes.append((vertice, adjacencias[0], adjacencias[1]))
        
        return lista_ligacoes


