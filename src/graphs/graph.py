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

    def mostrar_vizinhos(self, vertice):
        if vertice not in self.adjacencia:
            print("Erro: vértice não existe no grafo")
        else:
            return self.adjacencia[vertice]




