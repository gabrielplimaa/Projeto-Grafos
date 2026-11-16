from src.graphs.algorithms import dijkstra
from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa

import csv
from pathlib import Path

def exportar_resultado_dijkstra(nome_mapa, arestas_resultado):
    pasta_saida = Path("out/parte1")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_arquivo = pasta_saida / f"arestas_{nome_mapa}.csv"
    
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        writer.writerow(["origem", "destino", "peso"])
    
        # ex: [('A', 'B', 10), ('B', 'C', 5)]
        writer.writerows(arestas_resultado)

def test_exportacao_dijkstra():
    grafo = Grafo()

    origem = ""
    destino = ""
    
    distancias, antecessores = dijkstra(grafo, origem)
    
    arestas_caminho = []
    vertice_atual = destino
    
    if distancias[destino] != float('inf'):
        while antecessores[vertice_atual] is not None:
            antecessor = antecessores[vertice_atual]
            peso_aresta = distancias[vertice_atual] - distancias[antecessor]
            arestas_caminho.insert(0, (antecessor, vertice_atual, peso_aresta))
            vertice_atual = antecessor
            
    nome_do_mapa = "mapa_teste_1"
    
    exportar_resultado_dijkstra(nome_do_mapa, arestas_caminho)

    assert Path(f"out/parte1/arestas_{nome_do_mapa}.csv").exists()