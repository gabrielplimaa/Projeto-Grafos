# [IA] Gemini – orquestração de IO, medição de tempo (time.perf_counter) e exportação JSON da Parte 2.
import json
import time
from pathlib import Path
import pandas as pd

from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.graph import Grafo


def carregar_grafo_bitcoin(caminho_csv, fracao_nos=1.0, transformar_positivos=False):
    """Carrega o Bitcoin OTC em um Grafo dirigido do grupo.

    Se transformar_positivos=True, desloca os pesos w in [-10, +10] via
    w' = w + 10 (resultando em w' in [0, 20]) para uso no Dijkstra.
    """
    df = pd.read_csv(caminho_csv, names=["source", "target", "rating", "time"])

    if fracao_nos < 1.0:
        todos_nos = sorted(set(df["source"]).union(set(df["target"])))
        limite = max(10, int(len(todos_nos) * fracao_nos))
        nos_permitidos = set(todos_nos[:limite])
        df = df[df["source"].isin(nos_permitidos) & df["target"].isin(nos_permitidos)]

    grafo = Grafo()
    nos_adicionados = set()
    arestas_adicionadas = set()

    for row in df.itertuples(index=False):
        u, v, w = int(row.source), int(row.target), float(row.rating)
        if transformar_positivos:
            w = w + 10.0  # deslocamento linear de [-10, 10] para [0, 20]

        if u not in nos_adicionados:
            grafo.adicionar_no(u)
            nos_adicionados.add(u)
        if v not in nos_adicionados:
            grafo.adicionar_no(v)
            nos_adicionados.add(v)
        if (u, v) not in arestas_adicionadas:
            grafo.ligar(u, v, w)
            arestas_adicionadas.add((u, v))

    return grafo, df

def _contar_arestas(grafo):
    return sum(len(grafo.retornar_vizinhos(u)) for u in grafo.retornar_vertices())

def _reconstruir_caminho(antecessores, destino):
    if destino not in antecessores:
        return None
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = antecessores.get(atual)
    caminho.reverse()
    return caminho if len(caminho) > 1 else None


def _subgrafo_induzido(grafo, nos_subconjunto):
    sub = Grafo()
    permitidos = set(nos_subconjunto)
    nos_adicionados = set()
    arestas_adicionadas = set()

    for u in permitidos:
        if u not in nos_adicionados:
            sub.adicionar_no(u)
            nos_adicionados.add(u)
        for v, w in grafo.retornar_vizinhos(u):
            if v in permitidos:
                if v not in nos_adicionados:
                    sub.adicionar_no(v)
                    nos_adicionados.add(v)
                if (u, v) not in arestas_adicionadas:
                    sub.ligar(u, v, w)
                    arestas_adicionadas.add((u, v))
    return sub


def _tempo_medio(func, repeticoes=5):
    tempos = []
    ultimo_res = None
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        ultimo_res = func()
        tempos.append(time.perf_counter() - t0)
    return sum(tempos) / len(tempos), ultimo_res


def gerar_relatorio_parte2(caminho_dataset, pasta_saida="out/parte2"):
    caminho_csv = Path(caminho_dataset)
    if caminho_csv.is_dir():
        caminho_csv = next(caminho_csv.glob("*.csv"))

    pasta_out = Path(pasta_saida)
    pasta_out.mkdir(parents=True, exist_ok=True)

    print("Carregando grafo completo (pesos originais [-10, +10])...")
    grafo_orig, df = carregar_grafo_bitcoin(caminho_csv, fracao_nos=1.0, transformar_positivos=False)
    print("Carregando grafo transformado (pesos >= 0 via w' = w + 10)...")
    grafo_pos, _ = carregar_grafo_bitcoin(caminho_csv, fracao_nos=1.0, transformar_positivos=True)

    # Seleciona os nós mais ativos (maior grau de saída) como fontes/pares representativos
    top_nos = df.groupby("source").size().sort_values(ascending=False).index.astype(int).tolist()
    fontes_3 = top_nos[:3]
    pares_5 = [(top_nos[0], top_nos[1]), (top_nos[0], top_nos[2]),
               (top_nos[1], top_nos[3]), (top_nos[2], top_nos[4]),
               (top_nos[3], top_nos[5])]

    # 1. BFS e DFS em >= 3 fontes distintas
    print("Executando BFS e DFS em 3 fontes...")
    resultados_bfs = []
    resultados_dfs = []
    for src in fontes_3:
        t_bfs, (dist_bfs, _) = _tempo_medio(lambda s=src: bfs(grafo_orig, s), repeticoes=5)
        alcancados = [n for n, d in dist_bfs.items() if d != float("inf")]
        max_camada = max((d for d in dist_bfs.values() if d != float("inf")), default=0)
        resultados_bfs.append({
            "fonte": src,
            "nos_alcancados": len(alcancados),
            "camadas_max": int(max_camada),
            "tempo_medio_s": round(t_bfs, 6),
        })

        t_dfs, res_dfs = _tempo_medio(lambda s=src: dfs(grafo_orig, s), repeticoes=5)
        resultados_dfs.append({
            "fonte": src,
            "contagens_arcos": res_dfs["contagens"],
            "tem_ciclo": res_dfs["tem_ciclo"],
            "tempo_medio_s": round(t_dfs, 6),
        })

    # 2. Dijkstra em >= 5 pares origem-destino (com pesos >= 0)
    print("Executando Dijkstra em 5 pares (pesos transformados w' = rating + 10)...")
    resultados_dijkstra = []
    for u, v in pares_5:
        t_dij, (dist_d, ant_d) = _tempo_medio(lambda s=u: dijkstra(grafo_pos, s), repeticoes=5)
        caminho = _reconstruir_caminho(ant_d, v)
        resultados_dijkstra.append({
            "origem": u,
            "destino": v,
            "custo_transformado": dist_d.get(v, float("inf")),
            "saltos": len(caminho) - 1 if caminho else None,
            "caminho": caminho,
            "tempo_medio_s": round(t_dij, 6),
        })

    # 3. Bellman-Ford: (a) caso com peso negativo SEM ciclo negativo; (b) caso COM ciclo negativo
    print("Executando Bellman-Ford (sem ciclo negativo e com ciclo negativo)...")
    # (a) Subgrafo acíclico dirigido (DAG) ordenado pelo timestamp das avaliações -> garante arestas negativas sem ciclos
    df_ord = df.sort_values("time")
    sub_sem_ciclo = Grafo()
    nos_dag = set()
    arestas_dag = set()
    for row in df_ord.itertuples(index=False):
        u, v, w = int(row.source), int(row.target), float(row.rating)
        if u < v:
            if u not in nos_dag:
                sub_sem_ciclo.adicionar_no(u)
                nos_dag.add(u)
            if v not in nos_dag:
                sub_sem_ciclo.adicionar_no(v)
                nos_dag.add(v)
            if (u, v) not in arestas_dag:
                sub_sem_ciclo.ligar(u, v, w)
                arestas_dag.add((u, v))

    fonte_dag = min(sub_sem_ciclo.retornar_vertices())
    t_bf_sem, res_bf_sem = _tempo_medio(lambda: bellman_ford(sub_sem_ciclo, fonte_dag), repeticoes=5)
    alcancaveis_neg = {
        str(k): d for k, d in res_bf_sem["distancias"].items()
        if d < 0 and d != float("inf")
    }

    # (b) Subgrafo dos top 150 nós (inclui avaliações negativas mútuas -> ciclo negativo real)
    sub_com_ciclo = _subgrafo_induzido(grafo_orig, top_nos[:150])
    t_bf_com, res_bf_com = _tempo_medio(lambda: bellman_ford(sub_com_ciclo, fontes_3[0]), repeticoes=5)

    casos_bellman_ford = {
        "sem_ciclo_negativo": {
            "descricao": "Subgrafo dirigido acíclico (u < v) preservando ratings negativos originais",
            "ordem_V": len(sub_sem_ciclo.retornar_vertices()),
            "tamanho_E": _contar_arestas(sub_sem_ciclo),
            "fonte": fonte_dag,
            "tem_ciclo_negativo": res_bf_sem["tem_ciclo_negativo"],
            "qtd_nos_distancia_negativa": len(alcancaveis_neg),
            "exemplos_distancias_negativas": dict(list(alcancaveis_neg.items())[:5]),
            "tempo_medio_s": round(t_bf_sem, 6),
        },
        "com_ciclo_negativo": {
            "descricao": "Subgrafo induzido pelos 150 nós mais ativos com ratings originais [-10, +10]",
            "ordem_V": len(sub_com_ciclo.retornar_vertices()),
            "tamanho_E": _contar_arestas(sub_com_ciclo),
            "fonte": fontes_3[0],
            "tem_ciclo_negativo": res_bf_com["tem_ciclo_negativo"],
            "ciclo_detectado": res_bf_com["ciclo"],
            "custo_ciclo": res_bf_com["custo_ciclo"],
            "tempo_medio_s": round(t_bf_com, 6),
        },
    }

    # 4. Escalabilidade em 3 tamanhos: 10%, 50% e 100% dos nós (média de 5 execuções)
    print("Rodando benchmark de escalabilidade (10%, 50%, 100%)...")
    escalabilidade = []
    for frac in [0.10, 0.50, 1.00]:
        g_o, _ = carregar_grafo_bitcoin(caminho_csv, fracao_nos=frac, transformar_positivos=False)
        g_p, _ = carregar_grafo_bitcoin(caminho_csv, fracao_nos=frac, transformar_positivos=True)
        vertices = g_o.retornar_vertices()
        fonte_bench = max(vertices, key=lambda n: g_o.grau_saida(n))

        t_b, _ = _tempo_medio(lambda: bfs(g_o, fonte_bench), repeticoes=5)
        t_d, _ = _tempo_medio(lambda: dfs(g_o, fonte_bench), repeticoes=5)
        t_dij, _ = _tempo_medio(lambda: dijkstra(g_p, fonte_bench), repeticoes=5)

        # Para BF na escala 100%, usa subgrafo DAG ou amostra limitada se demorar muito,
        # mas aqui |V| ~ 5881 e |E| ~ 35592 roda em ~1-2s por execução!
        t_bf, _ = _tempo_medio(lambda: bellman_ford(g_o, fonte_bench), repeticoes=5)

        escalabilidade.append({
            "fracao_nos": frac,
            "ordem_V": len(vertices),
            "tamanho_E": _contar_arestas(g_o),
            "fonte": fonte_bench,
            "repeticoes": 5,
            "tempo_medio_s": {
                "BFS": round(t_b, 6),
                "DFS": round(t_d, 6),
                "Dijkstra": round(t_dij, 6),
                "Bellman_Ford": round(t_bf, 6),
            },
        })

    relatorio = {
        "dataset": {
            "nome": "SNAP Bitcoin OTC Trust Weighted Signed Network",
            "arquivo": caminho_csv.name,
            "ordem_V": len(grafo_orig.retornar_vertices()),
            "tamanho_E": _contar_arestas(grafo_orig),
            "transformacao_dijkstra": "w' = rating + 10 (deslocamento linear de [-10, +10] para [0, 20])",
        },
        "bfs_3_fontes": resultados_bfs,
        "dfs_3_fontes": resultados_dfs,
        "dijkstra_5_pares": resultados_dijkstra,
        "bellman_ford_casos": casos_bellman_ford,
        "escalabilidade_5_execucoes": escalabilidade,
    }

    arq_json = pasta_out / "parte2_report.json"
    with open(arq_json, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"Relatório salvo em: {arq_json}")
    return relatorio