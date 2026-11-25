"""Linha de comando do projeto.

Exemplos de uso:
    python -m src.cli --interactive --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/
    python -m src.cli --figuras --out ./out/parte1/
    python -m src.cli --graficos --out ./out/graficos_relatorio/

Sem --mapa, usa todos os mapas de data/mapas/ e data/mapas_grupo/.
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
        # [IA] Claude – depuração: o nó virtual ALVO não tem posição no mapa, então é pulado
        if estado == "ALVO":
            continue
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
    distancias_ida, _ = bfs(grafo, inicio)
    distancias_volta, _ = bfs(grafo.transposto(), "ALVO")

    armadilhas = [
        estado for estado in grafo.retornar_vertices()
        if distancias_ida[estado] != float('inf')
        and distancias_volta[estado] == float('inf')
        and estado != "ALVO"
    ]
    return armadilhas

# ==================================================================


def _executar(funcao, grafo, inicio, mapa):
    """Roda um algoritmo e converte o resultado (ou o erro) no formato do player."""
    try:
        resultado = funcao(grafo, inicio)
    except ValueError as erro:
        # O Dijkstra do grupo recusa peso negativo com ValueError.
        return execucao_status("recusado", str(erro))

    # O Bellman-Ford do grupo devolve um dicionário; BFS e Dijkstra, uma tupla.
    if isinstance(resultado, dict):
        if resultado["tem_ciclo_negativo"]:
            ciclo = resultado["ciclo"]
            mensagem = f"Ciclo negativo de custo {resultado['custo_ciclo']} com {len(ciclo) - 1} arcos"
            return execucao_status("ciclo_negativo", mensagem, ciclo=ciclo,
                                   custos_ciclo=custos_acumulados(grafo, ciclo))
        distancias, antecessores = resultado["distancias"], resultado["antecessores"]
    else:
        distancias, antecessores = resultado

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
        resultado = bellman_ford(grafo, inicio)
        if resultado["tem_ciclo_negativo"]:
            return []
        distancias, antecessores = resultado["distancias"], resultado["antecessores"]
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
    parser.add_argument("--alg", choices=["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"],
                        help="executa um algoritmo específico no(s) mapa(s)")
    parser.add_argument("--armadilhas", action="store_true",
                        help="identifica e exibe/salva os estados-armadilha do mapa")
    parser.add_argument("--fonte-consumivel", action="store_true",
                        help="torna a fonte '*' consumível (evita ciclo negativo no m06)")
    parser.add_argument("--interactive", action="store_true", help="gera labirinto_interativo.html")
    parser.add_argument("--figuras", action="store_true", help="gera as figuras da Seção 8 (PNG)")
    parser.add_argument("--graficos", action="store_true",
                        help="gera os 6 gráficos exploratórios e explanatórios do relatório (PNG)")
    parser.add_argument("--relatorios", action="store_true",
                        help="gera todos os relatórios e CSVs da Parte 1")
    parser.add_argument("--out", default="out/parte1", help="pasta de saída")
    parser.add_argument("--dataset", help="pasta ou arquivo CSV do dataset da Parte 2")
    parser.add_argument("--source", type=int, help="nó de origem para consulta na Parte 2")
    parser.add_argument("--target", type=int, help="nó de destino para consulta na Parte 2")
    parser.add_argument("--benchmark", action="store_true",
                        help="executa casos obrigatórios e benchmark da Parte 2")
    args = parser.parse_args(argv)

    if not (args.interactive or args.figuras or args.graficos or args.relatorios or args.alg or args.armadilhas or args.dataset):
        parser.error("use --alg, --armadilhas, --relatorios, --interactive, --figuras, --graficos ou --dataset")

    pasta_saida = Path(args.out)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Geração dos 6 gráficos exploratórios e explanatórios do relatório
    if args.graficos:
        from src.graficos_relatorio import gerar_graficos_relatorio
        caminho_ds = None
        if args.dataset:
            caminho_ds = Path(args.dataset)
            if caminho_ds.is_dir():
                caminho_ds = next(caminho_ds.glob("*.csv"))
        for saida in gerar_graficos_relatorio(pasta_saida, caminho_dataset=caminho_ds):
            print(f"Gerado: {saida}")
        if args.dataset and not (args.benchmark or args.alg):
            return

    # Execução da Parte 2 (dataset maior)
    if args.dataset:
        from src.parte2.experimentos import (carregar_grafo_bitcoin,
                                             gerar_relatorio_parte2,
                                             _reconstruir_caminho)

        caminho_ds = Path(args.dataset)
        if caminho_ds.is_dir():
            caminho_ds = next(caminho_ds.glob("*.csv"))

        if args.benchmark:
            gerar_relatorio_parte2(caminho_ds, args.out)

        if args.alg:
            if args.source is None:
                parser.error("informe --source ao rodar --alg com --dataset")
            usar_pos = (args.alg == "DIJKSTRA")
            grafo_ds, _ = carregar_grafo_bitcoin(caminho_ds, transformar_positivos=usar_pos)
            print(f"\n=== Dataset: {caminho_ds.name} | Algoritmo: {args.alg} | Origem: {args.source} ===")

            if args.alg == "BFS":
                dist, ant = bfs(grafo_ds, args.source)
                if args.target is not None:
                    cam = _reconstruir_caminho(ant, args.target)
                    print(f"Saltos até {args.target}: {dist.get(args.target)} | Caminho: {cam}")
                else:
                    alc = sum(1 for d in dist.values() if d != float("inf"))
                    print(f"Nós alcançados: {alc}")
            elif args.alg == "DFS":
                from src.graphs.algorithms import dfs
                res_dfs = dfs(grafo_ds, args.source)
                print(f"Contagens: {res_dfs['contagens']} | Tem ciclo: {res_dfs['tem_ciclo']}")
            elif args.alg == "DIJKSTRA":
                dist, ant = dijkstra(grafo_ds, args.source)
                if args.target is not None:
                    cam = _reconstruir_caminho(ant, args.target)
                    print(f"Custo (w'=w+10) até {args.target}: {dist.get(args.target)} | Caminho: {cam}")
            elif args.alg == "BELLMAN_FORD":
                res_bf = bellman_ford(grafo_ds, args.source)
                print(f"Tem ciclo negativo: {res_bf['tem_ciclo_negativo']}")
                if res_bf["tem_ciclo_negativo"]:
                    print(f"Ciclo ({res_bf['custo_ciclo']}): {res_bf['ciclo']}")
                elif args.target is not None:
                    cam = _reconstruir_caminho(res_bf["antecessores"], args.target)
                    print(f"Custo até {args.target}: {res_bf['distancias'].get(args.target)} | Caminho: {cam}")
        return

    # Execução direta de --alg ou --armadilhas (usado no mapa surpresa e no m06)
    if args.alg or args.armadilhas:
        from src.graphs.algorithms import dfs
        from src.graphs.estados import numerar_bonus, rotulo

        for arq in _arquivos_de_mapa(args.mapa):
            mapa = ler_mapa(arq)
            bonus_idx = numerar_bonus(mapa)
            grafo, inicio = construir_grafo_estados(mapa, fonte_consumivel=args.fonte_consumivel)
            print(f"\n=== Mapa: {arq.stem} (fonte_consumivel={args.fonte_consumivel}) ===")

            if args.alg:
                if args.alg == "DFS":
                    res_dfs = dfs(grafo, inicio)
                    print(f"DFS -> Contagens: {res_dfs['contagens']} | Tem ciclo: {res_dfs['tem_ciclo']}")
                else:
                    mapa_alg = {"BFS": bfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}
                    res = _executar(mapa_alg[args.alg], grafo, inicio, mapa)
                    print(f"{args.alg} -> Status: {res['status']}")
                    if res["status"] == "ok":
                        passos_dict = res["passos"]
                        caminho_fmt = [
                            f"({p['pos'][0]},{p['pos'][1]})|{p['chaves'] or '-'}|{{{','.join(map(str, p['bonus']))}}}"
                            for p in passos_dict
                        ]
                        print(f"Passos: {len(caminho_fmt) - 1} | Custo: {passos_dict[-1]['custo']}")
                        print(f"Caminho: {' -> '.join(caminho_fmt)}")
                    else:
                        print(f"Detalhe: {res.get('mensagem', '')}")

            if args.armadilhas:
                lista_arm = estados_armadilha(grafo, inicio)
                arm_fmt = [rotulo(e, bonus_idx=bonus_idx, ignorar_nao_bonus=args.fonte_consumivel) for e in lista_arm]
                print(f"Estados-armadilha ({len(arm_fmt)}): {arm_fmt}")

    if args.relatorios:
        gerar_relatorios(args.out)
        print(f"Gerados: relatórios completos da Parte 1 em {args.out}")

    if args.interactive:
        mapas = montar_dados_interativo(_arquivos_de_mapa(args.mapa))
        saida = gerar_html(mapas, pasta_saida / "labirinto_interativo.html")
        print(f"Gerado: {saida} ({len(mapas)} mapas)")

    if args.figuras:
        for saida in gerar_figuras(args.out):
            print(f"Gerado: {saida}")


if __name__ == "__main__":
    main()