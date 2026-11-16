from src.graphs.algorithms import dfs

import csv
from pathlib import Path

def exportar_resultado_""(nome_mapa, arestas_resultado):
    pasta_saida = Path("out/parte1")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_arquivo = pasta_saida / f"arestas_{nome_mapa}.csv"
    
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        writer.writerow(["origem", "destino", "peso"])
    
        # ex: [('A', 'B', 10), ('B', 'C', 5)]
        writer.writerows(arestas_resultado)

def test_exportacao_""():
    # ... aqui você chama seu algoritmo de dfs ...
    # resultado = dijkstra(grafo, origem, destino)
    
    # Mock do resultado para o exemplo (lista de arestas do caminho)
    arestas_caminho = [
        ("A", "B", 4),
        ("B", "C", 2),
        ("C", "D", 5)
    ]
    
    nome_do_mapa = "mapa_teste_1"
    
    # Chama a função de exportação
    exportar_resultado_""(nome_do_mapa, arestas_caminho)
    
    # Verifica se o arquivo foi realmente criado no teste
    assert Path(f"out/parte1/arestas_{nome_do_mapa}.csv").exists()