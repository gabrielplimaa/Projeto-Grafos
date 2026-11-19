from src.graphs.algorithms import dijkstra
from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa

import csv
from pathlib import Path

def exportar_resultado_dijkstra(nome_mapa, arestas_resultado):
    pasta_saida = Path("out/parte1")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_arquivo = pasta_saida / f"graus_{nome_mapa}.csv"
    
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        writer.writerow(["origem", "destino", "peso"])
    
        # ex: [('A', 'B', 10), ('B', 'C', 5)]
        writer.writerows(arestas_resultado)

def test_exportacao_dijkstra():
    nome_do_mapa = "m01_terreno"
    caminho_arquivo_mapa = f"data/mapas/{nome_do_mapa}.txt"
    linhas_mapa = ler_mapa(caminho_arquivo_mapa)
    
    grafo = Grafo()
    
    origem = None
    destino = None
    
    pesos_terreno = {
        '.': 1, 'S': 1, 'G': 1, 
        ',': 2, '~': 5, 
    }

    for y, linha in enumerate(linhas_mapa):
        for x, char in enumerate(linha):
            if char != "#":
                coord = f"{y},{x}"
                grafo.adicionar_no(coord)
                
                if char == "S":
                    origem = coord
                elif char == "G" and destino is None:
                    destino = coord

    linhas_qtd = len(linhas_mapa)
    colunas_qtd = len(linhas_mapa[0])

    for y, linha in enumerate(linhas_mapa):
        for x, char in enumerate(linha):
            if char != "#":
                coord_atual = f"{y},{x}"
                movimentos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                
                for dy, dx in movimentos:
                    ny, nx = y + dy, x + dx
                    
                    if 0 <= ny < linhas_qtd and 0 <= nx < colunas_qtd:
                        vizinho_char = linhas_mapa[ny][nx]
                        
                        if vizinho_char != "#":
                            coord_vizinho = f"{ny},{nx}"
                            peso_aresta = pesos_terreno.get(vizinho_char, 1)
                            
                            grafo.ligar(coord_atual, coord_vizinho, peso_aresta)
    
    assert origem is not None, "Origem 'S' não encontrada no mapa."
    assert destino is not None, "Destino 'G' não encontrado no mapa."
    
    distancias, antecessores = dijkstra(grafo, origem)
    arestas_caminho = []
    vertice_atual = destino
    
    if distancias[destino] != float('inf'):
        while antecessores[vertice_atual] is not None:
            antecessor = antecessores[vertice_atual]
            peso_aresta = distancias[vertice_atual] - distancias[antecessor]
            arestas_caminho.insert(0, (antecessor, vertice_atual, peso_aresta))
            vertice_atual = antecessor
            
    exportar_resultado_dijkstra(nome_do_mapa, arestas_caminho)
    
    ficheiro_exportado = Path(f"out/parte1/graus_{nome_do_mapa}.csv")
    assert ficheiro_exportado.exists()


if __name__ == "__main__":
    test_exportacao_dijkstra()
    print("Teste concluído e arquivo exportado!")