from src.graphs.algorithms import dfs
from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa

import json
from pathlib import Path

def exportar_resultado_dfs(nome_mapa, contagens_arestas):
    pasta_saida = Path("out/parte1")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_arquivo = pasta_saida / f"graus_{nome_mapa}.csv"
    
    with open(caminho_arquivo, mode='w', encoding='utf-8') as arquivo_json:
        json.dump(contagens_arestas, arquivo_json, indent=4)

def test_exportacao_dfs():
    nome_do_mapa = "m01_terreno"
    caminho_arquivo_mapa = f"data/mapas/{nome_do_mapa}.txt"
    linhas_mapa = ler_mapa(caminho_arquivo_mapa)
    
    grafo = Grafo()
    origem = None
    
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
    
    contagens = dfs(grafo, origem)
    assert isinstance(contagens, dict)
    assert set(contagens.keys()) == {"arvore", "retorno", "avanco", "cruzamento"}
            
    exportar_resultado_dfs(nome_do_mapa, contagens)
    
    ficheiro_exportado = Path(f"out/parte1/graus_{nome_do_mapa}.csv")
    assert ficheiro_exportado.exists()

if __name__ == "__main__":
    test_exportacao_dfs()
    print("Teste DFS concluído e arquivo exportado!")