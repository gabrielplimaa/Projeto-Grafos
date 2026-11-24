"""Linha de comando do projeto.

Por enquanto estão montadas as opções --interactive (labirinto interativo) e
--figuras (figuras da Seção 8):

    python -m src.cli --interactive --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/
    python -m src.cli --figuras --out ./out/parte1/

Sem --mapa, usa todos os mapas de data/mapas/ e data/mapas_grupo/.
As demais opções do enunciado (--alg, --armadilhas, --fonte-consumivel, --dataset...)
entram aqui depois, pelos outros pacotes.
"""

# [IA] Claude – sintaxe de argparse e orquestração de IO (leitura dos mapas, tratamento
# dos erros dos algoritmos, chamada de gerar_html e das funções de desenho das figuras). As funções marcadas "PARTE DO GRUPO"
# não foram escritas pela IA: elas resolvem os mapas e são responsabilidade de P1/P2.

import argparse
from pathlib import Path

from src.graphs.algorithms import bellman_ford, bfs, dijkstra
from src.graphs.estados import construir_grafo_estados
from src.graphs.main import gerar_relatorios
from src.graphs.io import ler_mapa
from src.labirinto_interativo import execucao_ok, execucao_status, gerar_html
from src.viz import (desenhar_arvore_bfs, desenhar_camadas, desenhar_heatmap_multiplicidade,
                     desenhar_percurso)

PASTAS_PADRAO = [Path("data/mapas"), Path("data/mapas_grupo")]
ALGORITMOS = {"BFS": bfs, "Dijkstra": dijkstra, "Bellman-Ford": bellman_ford}


# ===================== PARTE DO GRUPO (P1/P2) =====================

def estado_final(grafo, mapa, distancias):
    melhor = None
    for estado in grafo.retornar_vertices():
        (i, j) = estado[0]
        if mapa[i][j] == "G" and distancias[estado] != float('inf'):
            if melhor is None or distancias[estado] < distancias[melhor]:
                melhor = estado
    return melhor


def reconstruir_caminho(antecessores, destino):
    caminho = []
    atual = destino 
    while atual is not None:
        caminho.append(atual)
        atual = antecessores.get(atual)
    caminho.reverse()
    return caminho

def custos_acumulados(grafo, caminho):
   custos = [0]
   for i in range(1, len(caminho)):
       anterior = caminho[i - 1]
       atual = caminho[i]
       for vizinho, custo in grafo.retornar_vizinhos(anterior):
           if vizinho == atual:
               custos.append(custos[-1] + custo)
               break
   return custos
def estados_armadilha(grafo, inicio):
    """Estados alcançáveis dos quais o ALVO é inalcançável (busca no grafo transposto).

    Enquanto não estiver implementada, devolve lista vazia e o HTML não realça nada.
    """
    return []

# ==================================================================


def _executar(funcao, grafo, inicio, mapa):
    """Roda um algoritmo e converte o resultado (ou o erro) no formato do player."""
    try:
        distancias, antecessores = funcao(grafo, inicio)
    except ValueError as erro:
        mensagem = str(erro)
        # Os algoritmos do grupo sinalizam recusa e ciclo negativo com ValueError;
        # a mensagem diferencia os dois casos.
        if "ciclo" in mensagem.lower():
            return execucao_status("ciclo_negativo", mensagem)
        return execucao_status("recusado", mensagem)

    destino = estado_final(grafo, mapa, distancias)
    if destino is None:
        return execucao_status("sem_solucao", "Nenhum estado em G é alcançável a partir do início")
    caminho = reconstruir_caminho(antecessores, destino)
    return execucao_ok(caminho, custos_acumulados(grafo, caminho))


def _arquivos_de_mapa(caminhos):
    if caminhos:
        return [Path(c) for c in caminhos]
    arquivos = []
    for pasta in PASTAS_PADRAO:
        arquivos.extend(sorted(pasta.glob("*.txt")))
    return arquivos


def montar_dados_interativo(arquivos):
    """Lê cada mapa, monta o grafo de estados e roda os 3 algoritmos de caminho."""
    mapas = {}
    for arquivo in arquivos:
        try:
            mapa = ler_mapa(arquivo)
        except ValueError as erro:
            # Ex.: os mapas do grupo ainda vazios. Avisa e segue com os outros.
            print(f"Ignorando {arquivo}: {erro}")
            continue
        grafo, inicio = construir_grafo_estados(mapa)
        mapas[arquivo.stem] = {
            "grade": mapa,
            "execucoes": {nome: _executar(f, grafo, inicio, mapa) for nome, f in ALGORITMOS.items()},
            "armadilhas": estados_armadilha(grafo, inicio),
        }
    return mapas


def _caminho_menor_custo(grafo, inicio, mapa):
    """Caminho de menor custo com as funções do grupo: Dijkstra, ou Bellman-Ford se houver peso negativo."""
    try:
        distancias, antecessores = dijkstra(grafo, inicio)
    except ValueError:
        distancias, antecessores = bellman_ford(grafo, inicio)
    destino = estado_final(grafo, mapa, distancias)
    return reconstruir_caminho(antecessores, destino) if destino is not None else []


def gerar_figuras(pasta_saida):
    """Gera as figuras da Seção 8 do enunciado em pasta_saida."""
    pasta_saida = Path(pasta_saida)
    pasta_mapas = Path("data/mapas")
    gerados = []

    for nome in ("m03_tres_chaves", "m08_grande"):
        mapa = ler_mapa(pasta_mapas / f"{nome}.txt")
        grafo, inicio = construir_grafo_estados(mapa)
        caminho = _caminho_menor_custo(grafo, inicio, mapa)
        curto = nome.split("_")[0]
        gerados.append(desenhar_percurso(mapa, caminho, pasta_saida / f"percurso_{curto}.png",
                                         f"Percurso de menor custo em {curto} (cor muda a cada chave)"))

    mapa = ler_mapa(pasta_mapas / "m02_uma_chave.txt")
    grafo, inicio = construir_grafo_estados(mapa)
    gerados.append(desenhar_camadas(grafo, mapa, pasta_saida / "camadas_m02.png",
                                    "Grafo de estados do m02 em camadas (uma por conjunto de chaves)"))
    distancias, antecessores = bfs(grafo, inicio)
    gerados.append(desenhar_arvore_bfs(grafo, mapa, distancias, antecessores, pasta_saida / "arvore_bfs_m02.png",
                                       "Árvore BFS de estados do m02"))

    mapa = ler_mapa(pasta_mapas / "m08_grande.txt")
    grafo, _ = construir_grafo_estados(mapa)
    gerados.append(desenhar_heatmap_multiplicidade(grafo, mapa, pasta_saida / "heatmap_multiplicidade_m08.png",
                                                   "Multiplicidade das casas do m08 (estados por casa)"))
    return gerados


def main(argv=None):
    parser = argparse.ArgumentParser(description="Projeto de Teoria dos Grafos: labirinto com chaves")
    parser.add_argument("--mapa", nargs="+", help="um ou mais arquivos de mapa (.txt)")
    parser.add_argument("--interactive", action="store_true", help="gera labirinto_interativo.html")
    parser.add_argument("--figuras", action="store_true", help="gera as figuras da Seção 8 (PNG)")
    parser.add_argument("--relatorios", action="store_true",
                        help="gera arestas, graus, metricas_global.json e camadas.json (Seções 2 e 3)")
    parser.add_argument("--out", default="out/parte1", help="pasta de saída")
    args = parser.parse_args(argv)

    if not (args.interactive or args.figuras or args.relatorios):
        parser.error("use --relatorios, --interactive ou --figuras")

    if args.relatorios:
        gerar_relatorios(args.out)
        print(f"Gerados: arestas, graus, metricas_global.json e camadas.json em {args.out}")

    if args.interactive:
        mapas = montar_dados_interativo(_arquivos_de_mapa(args.mapa))
        saida = gerar_html(mapas, Path(args.out) / "labirinto_interativo.html")
        print(f"Gerado: {saida} ({len(mapas)} mapas)")
    if args.figuras:
        for saida in gerar_figuras(args.out):
            print(f"Gerado: {saida}")


if __name__ == "__main__":
    main()
