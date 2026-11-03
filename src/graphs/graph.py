class Grafo:
    def __init__(self):
        self.adjacencia = {

        }

    def adicionar_no(self, vertice):
        if vertice not in self.adjacencia:
            self.adjacencia[vertice] = []
        else:
            print("Erro: vértice já existe")

    def ligar(self, origem, destino, peso):
        if origem not in self.adjacencia or destino not in self.adjacencia:
            print("Erro: Não existe um dos vértices no grafo")
            return

        self.adjacencia[origem].append([destino, peso])

    def retornar_vizinhos(self, vertice):
        if vertice not in self.adjacencia:
            print("Erro: vértice não existe no grafo")
        else:
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


