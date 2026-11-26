import csv
import json
from pathlib import Path
from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.io import ler_mapa
from src.graphs.estados import (
    construir_grafo_posicoes,
    construir_grafo_estados,
    numerar_bonus,
    rotulo,
)


def calcular_densidade(num_vertices: int, num_arcos: int) -> float:
    if num_vertices < 2:
        return 0.0
    return num_arcos / (num_vertices * (num_vertices - 1))


def contar_elementos_teto(mapa: list[str]) -> tuple[int, int]:
    chaves_distintas = set()
    bonus_unicos = 0
    for linha in mapa:
        for char in linha:
            if char in "abcd":
                chaves_distintas.add(char)
            elif char == "+":
                bonus_unicos += 1
    return len(chaves_distintas), bonus_unicos


def formatar_estado(estado, bonus_idx: dict) -> str:
    return rotulo(estado, bonus_idx=bonus_idx)


def calcular_camadas_e_transicoes(grafo_estados, mapa: list[str]) -> tuple[dict, dict]:
    vertices = [v for v in grafo_estados.retornar_vertices() if v != "ALVO"]
    arcos = [
        (u, v, peso)
        for u, v, peso in grafo_estados.retornar_ligacoes()
        if u != "ALVO" and v != "ALVO"
    ]

    vertices_por_camada: dict[frozenset, set] = {}
    for v in vertices:
        chaves = v[1]
        vertices_por_camada.setdefault(chaves, set()).add(v)

    arcos_internos_por_camada: dict[frozenset, int] = {c: 0 for c in vertices_por_camada}
    qtd_arcos_entre_camadas = 0
    casas_geradoras_transicao = set()

    for origem, destino, _peso in arcos:
        chaves_orig = origem[1]
        chaves_dest = destino[1]

        if chaves_orig == chaves_dest:
            arcos_internos_por_camada[chaves_orig] += 1
        else:
            qtd_arcos_entre_camadas += 1
            pos_dest = destino[0]
            simbolo = mapa[pos_dest[0]][pos_dest[1]]
            casas_geradoras_transicao.add((pos_dest[0], pos_dest[1], simbolo))

    metricas_camadas = {}
    for chaves in sorted(vertices_por_camada.keys(), key=lambda c: (len(c), sorted(c))):
        nome_camada = "".join(sorted(chaves)) if chaves else "sem_chaves"
        ordem = len(vertices_por_camada[chaves])
        tamanho = arcos_internos_por_camada[chaves]
        densidade = calcular_densidade(ordem, tamanho)

        metricas_camadas[nome_camada] = {
            "chaves": sorted(chaves),
            "ordem": ordem,
            "tamanho": tamanho,
            "densidade": round(densidade, 6),
        }

    casas_ordenadas = [
        {"linha": i, "coluna": j, "simbolo": simb}
        for i, j, simb in sorted(casas_geradoras_transicao)
    ]

    info_arcos_entre_camadas = {
        "quantidade_arcos": qtd_arcos_entre_camadas,
        "casas_geradoras": casas_ordenadas,
    }

    return metricas_camadas, info_arcos_entre_camadas


def calcular_graus_e_rankings(grafo_estados, mapa: list[str], bonus_idx: dict) -> dict:
    # [IA] Claude (Anthropic) – Seção 4: maiores graus, becos e multiplicidade das casas
    vertices = [v for v in grafo_estados.retornar_vertices() if v != "ALVO"]
    grau_entrada = {v: 0 for v in vertices}
    grau_saida = {v: 0 for v in vertices}
    for origem, destino, _peso in grafo_estados.retornar_ligacoes():
        if origem != "ALVO" and destino != "ALVO":
            grau_saida[origem] += 1
            grau_entrada[destino] += 1

    def ordem_de_leitura(estado):
        (i, j), _chaves, _bonus = estado
        return (i, j, formatar_estado(estado, bonus_idx))

    maior_saida = min(vertices, key=lambda v: (-grau_saida[v], ordem_de_leitura(v)))
    maior_entrada = min(vertices, key=lambda v: (-grau_entrada[v], ordem_de_leitura(v)))

    becos = sorted(
        (v for v in vertices if grau_saida[v] == 0 and mapa[v[0][0]][v[0][1]] != "G"),
        key=ordem_de_leitura,
    )

    multiplicidade = {}
    for (i, j), _chaves, _bonus in vertices:
        multiplicidade[(i, j)] = multiplicidade.get((i, j), 0) + 1
    maxima = max(multiplicidade.values())
    casas_maximas = sorted(casa for casa, qtd in multiplicidade.items() if qtd == maxima)

    return {
        "maior_grau_saida": {"estado": formatar_estado(maior_saida, bonus_idx), "grau": grau_saida[maior_saida]},
        "maior_grau_entrada": {"estado": formatar_estado(maior_entrada, bonus_idx), "grau": grau_entrada[maior_entrada]},
        "becos": [formatar_estado(v, bonus_idx) for v in becos],
        "multiplicidade": {
            "maxima": maxima,
            "qtd_casas_com_maxima": len(casas_maximas),
            "casas_com_maxima": [{"linha": i, "coluna": j, "simbolo": mapa[i][j]} for i, j in casas_maximas],
        },
    }

def exportar_graus_csv(nome_mapa: str, grafo_estados, bonus_idx: dict, pasta_saida: Path) -> None:
    vertices = [v for v in grafo_estados.retornar_vertices() if v != "ALVO"]
    arcos = [
        (u, v, peso)
        for u, v, peso in grafo_estados.retornar_ligacoes()
        if u != "ALVO" and v != "ALVO"
    ]

    grau_entrada = {v: 0 for v in vertices}
    grau_saida = {v: 0 for v in vertices}

    for origem, destino, _peso in arcos:
        grau_saida[origem] += 1
        grau_entrada[destino] += 1

    caminho_csv = pasta_saida / f"graus_{nome_mapa}.csv"
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["estado", "grau_entrada", "grau_saida"])
        for v in vertices:
            writer.writerow([formatar_estado(v, bonus_idx), grau_entrada[v], grau_saida[v]])


def exportar_arestas_csv(nome_mapa: str, grafo_estados, bonus_idx: dict, pasta_saida: Path, mapa: list[str]) -> None:
    arcos = [
        (u, v, peso)
        for u, v, peso in grafo_estados.retornar_ligacoes()
        if u != "ALVO" and v != "ALVO"
    ]

    caminho_csv = pasta_saida / f"arestas_{nome_mapa}.csv"
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["origem", "destino", "movimento", "casa_destino", "peso"])
        for origem, destino, peso in arcos:
            mov = grafo_estados.retornar_movimento(origem, destino)
            (dest_i, dest_j), _, _ = destino
            writer.writerow([
                formatar_estado(origem, bonus_idx),
                formatar_estado(destino, bonus_idx),
                mov,
                 mapa[dest_i][dest_j],
                peso,
            ])

def _validar_caminho_g_pos(mapa: list[str], caminho: list[tuple[int, int]]) -> tuple[bool, str]:
    """Verifica se um caminho em G_pos (porta como chão) passa por porta sem ter pego a chave."""
    chaves_coletadas = set()
    for i, j in caminho:
        celula = mapa[i][j]
        if celula in "abcd":
            chaves_coletadas.add(celula)
        elif celula in "ABCD":
            if celula.lower() not in chaves_coletadas:
                return False, f"Atravessou porta '{celula}' em ({i},{j}) sem a chave '{celula.lower()}'"
    return True, "Caminho válido respeitando portas e chaves"


def exportar_saidas_caminhos_e_analises(caminhos_mapas: list[Path], pasta_saida: Path) -> None:
    from src.cli import custos_acumulados, estado_final, estados_armadilha, reconstruir_caminho
    
    linhas_solucoes = []
    linhas_comparacao = []
    linhas_dfs = []

    for caminho_mapa in caminhos_mapas:
        nome_mapa = caminho_mapa.stem
        mapa = ler_mapa(str(caminho_mapa))
        bonus_idx = numerar_bonus(mapa)
        g_est, inicio = construir_grafo_estados(mapa)

        # --- 1. SOLUÇÕES (BFS, Dijkstra, Bellman-Ford) ---
        # --- 1. SOLUÇÕES (BFS, Dijkstra, Bellman-Ford) ---
        for nome_alg, func_alg in [("BFS", bfs), ("Dijkstra", dijkstra), ("Bellman-Ford", bellman_ford)]:
            try:
                res = func_alg(g_est, inicio)
            except ValueError:
                linhas_solucoes.append([nome_mapa, nome_alg, "", "", "RECUSA", ""])
                continue

            if isinstance(res, dict):
                if res["tem_ciclo_negativo"]:
                    ciclo_fmt = [formatar_estado(v, bonus_idx) for v in res["ciclo"]]
                    linhas_solucoes.append([
                        nome_mapa,
                        nome_alg,
                        len(ciclo_fmt) - 1,
                        res["custo_ciclo"],
                        "CICLO_NEGATIVO",
                        " -> ".join(ciclo_fmt),
                    ])
                    if nome_mapa == "m06_fonte":
                        with open(pasta_saida / "ciclo_negativo_m06.json", "w", encoding="utf-8") as f:
                            json.dump({
                                "mapa": nome_mapa,
                                "custo_ciclo": res["custo_ciclo"],
                                "ciclo": ciclo_fmt,
                            }, f, indent=4, ensure_ascii=False)
                    continue
                distancias, antecessores = res["distancias"], res["antecessores"]
            else:
                distancias, antecessores = res

            destino = estado_final(g_est, mapa, distancias)
            if destino is None:
                linhas_solucoes.append([nome_mapa, nome_alg, "", "", "SEM_SOLUCAO", ""])
            else:
                caminho = reconstruir_caminho(antecessores, destino)
                custos = custos_acumulados(g_est, caminho)
                passos = len(caminho) - 1
                custo_total = custos[-1]
                caminho_fmt = " -> ".join(formatar_estado(v, bonus_idx) for v in caminho)

                linhas_solucoes.append([
                    nome_mapa,
                    nome_alg,
                    passos,
                    custo_total,
                    "OK",
                    caminho_fmt,
                ])

                if nome_mapa == "m03_tres_chaves" and nome_alg == "Bellman-Ford":
                    with open(pasta_saida / "percurso_m03.json", "w", encoding="utf-8") as f:
                        json.dump({
                            "mapa": nome_mapa,
                            "custo_total": custo_total,
                            "passos": passos,
                            "percurso": [formatar_estado(v, bonus_idx) for v in caminho],
                            "custos_acumulados": custos,
                        }, f, indent=4, ensure_ascii=False)

        # --- 2. DFS CLASSIFICAÇÃO ---
        res_dfs = dfs(g_est, inicio)
        c_dfs = res_dfs["contagens"]
        linhas_dfs.append([
            nome_mapa,
            c_dfs["arvore"],
            c_dfs["retorno"],
            c_dfs["avanco"],
            c_dfs["cruzamento"],
            res_dfs["tem_ciclo"],
        ])
        # --- 3. ARMADILHAS (m04 e m07) ---
        if nome_mapa in ("m04_esteiras", "m07_impossivel"):
            armadilhas = estados_armadilha(g_est, inicio)
            curto = nome_mapa.split("_")[0]
            with open(pasta_saida / f"armadilhas_{curto}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["estado", "posicao", "chaves", "bonus"])
                for est in armadilhas:
                    pos, chaves, bonus = est
                    chaves_str = "".join(sorted(chaves)) if chaves else "-"
                    bonus_str = "{" + ",".join(str(bonus_idx[b]) for b in sorted(bonus)) + "}"
                    writer.writerow([formatar_estado(est, bonus_idx), f"({pos[0]},{pos[1]})", chaves_str, bonus_str])

        # --- 4. COMPARAÇÃO DE MODELAGENS (m02, m03, m04) ---
        if nome_mapa in ("m02_uma_chave", "m03_tres_chaves", "m04_esteiras"):
            pos_s = next((i, j) for i, linha in enumerate(mapa) for j, c in enumerate(linha) if c == "S")
            pos_g = next((i, j) for i, linha in enumerate(mapa) for j, c in enumerate(linha) if c == "G")

            # (a) G_pos porta como chão
            g_pos_chao = construir_grafo_posicoes(mapa, porta_como_parede=False)
            dist_a, pred_a = bfs(g_pos_chao, pos_s)
            if dist_a.get(pos_g, float("inf")) != float("inf"):
                cam_a = reconstruir_caminho(pred_a, pos_g)
                valido_a, obs_a = _validar_caminho_g_pos(mapa, cam_a)
                linhas_comparacao.append([nome_mapa, "G_pos_porta_chao", len(cam_a) - 1, valido_a, obs_a])
            else:
                linhas_comparacao.append([nome_mapa, "G_pos_porta_chao", -1, False, "Sem caminho até G"])

            # (b) G_pos porta como parede
            g_pos_parede = construir_grafo_posicoes(mapa, porta_como_parede=True)
            dist_b, pred_b = bfs(g_pos_parede, pos_s)
            if dist_b.get(pos_g, float("inf")) != float("inf"):
                cam_b = reconstruir_caminho(pred_b, pos_g)
                linhas_comparacao.append([nome_mapa, "G_pos_porta_parede", len(cam_b) - 1, True, "Caminho sem passar por portas"])
            else:
                linhas_comparacao.append([nome_mapa, "G_pos_porta_parede", -1, False, "Bloqueado por porta tratada como parede"])

            # (c) G_est
            dist_c, pred_c = bfs(g_est, inicio)
            dest_c = estado_final(g_est, mapa, dist_c)
            if dest_c is not None:
                cam_c = reconstruir_caminho(pred_c, dest_c)
                linhas_comparacao.append([nome_mapa, "G_est", len(cam_c) - 1, True, "Modelagem completa com estados"])
            else:
                linhas_comparacao.append([nome_mapa, "G_est", -1, False, "Sem solução em G_est"])

    # Escrita dos CSVs consolidados
    with open(pasta_saida / "solucoes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mapa", "algoritmo", "passos", "custo", "status", "caminho"])
        writer.writerows(linhas_solucoes)

    with open(pasta_saida / "dfs_classificacao.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mapa", "arvore", "retorno", "avanco", "cruzamento", "tem_ciclo"])
        writer.writerows(linhas_dfs)

    with open(pasta_saida / "comparacao_modelagem.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mapa", "abordagem", "passos", "caminho_valido", "observacao"])
        writer.writerows(linhas_comparacao)
# [IA] Claude – revisão e depuração: a função foi escrita pelo grupo. A IA sugeriu usar a
# custos_acumulados do grupo no lugar de uma função auxiliar que repetia o mesmo cálculo e
# tirar as checagens de tupla, porque o bellman_ford do grupo sempre devolve um dicionário.
def exportar_bellman_ford_m05(pasta_saida):
    """Seção 6: ciclo negativo do m05 no G_pos (+ = -4 fixo) e resposta finita no G_est."""
    from src.cli import custos_acumulados, estado_final, reconstruir_caminho

    caminho_mapa = Path("data/mapas/m05_bonus.txt")
    mapa = ler_mapa(str(caminho_mapa))
    bonus_idx = numerar_bonus(mapa)

    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    def formatar_posicao(posicao):
        # No G_pos o vértice é só (i, j); o rotulo() espera um estado, então o texto é montado aqui.
        return f"({posicao[0]},{posicao[1]})"

    # G_pos: o bônus "+" vale -4 toda vez que se entra nele
    g_pos = construir_grafo_posicoes(mapa)
    inicio_pos = next(
        (i, j)
        for i, linha in enumerate(mapa)
        for j, celula in enumerate(linha)
        if celula == "S"
    )
    res_pos = bellman_ford(g_pos, inicio_pos)

    if res_pos["tem_ciclo_negativo"]:
        ciclo_pos = res_pos["ciclo"]
        dados_pos = {
            "tem_ciclo_negativo": True,
            "ciclo": [formatar_posicao(pos) for pos in ciclo_pos],
            "custo_ciclo": res_pos["custo_ciclo"],
            "custos_acumulados": custos_acumulados(g_pos, ciclo_pos),
        }
    else:
        dados_pos = {
            "tem_ciclo_negativo": False,
            "ciclo": [],
            "custo_ciclo": None,
            "custos_acumulados": [],
        }

    # G_est: cada bônus só vale -4 uma vez, porque o estado guarda os bônus consumidos
    g_est, inicio = construir_grafo_estados(mapa)
    res_est = bellman_ford(g_est, inicio)

    dados_est = {
        "tem_ciclo_negativo": res_est["tem_ciclo_negativo"],
        "custo": None,
        "passos": None,
        "percurso": [],
        "custos_acumulados": [],
    }
    if not res_est["tem_ciclo_negativo"]:
        destino = estado_final(g_est, mapa, res_est["distancias"])
        if destino is not None:
            caminho = reconstruir_caminho(res_est["antecessores"], destino)
            custos = custos_acumulados(g_est, caminho)
            dados_est.update({
                "custo": custos[-1],
                "passos": len(caminho) - 1,
                "percurso": [formatar_estado(estado, bonus_idx) for estado in caminho],
                "custos_acumulados": custos,
            })

    dados = {"G_pos": dados_pos, "G_est": dados_est}
    caminho_saida = pasta_saida / "bellman_ford_m05.json"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    return caminho_saida

def gerar_relatorios(pasta_saida="out/parte1") -> None:
    pastas_mapas = [Path("data/mapas"), Path("data/mapas_grupo")]
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    metricas_global_todos = {}
    camadas_todos = {}

    caminhos = []
    for pasta in pastas_mapas:
        if pasta.exists():
            caminhos.extend(sorted(pasta.glob("*.txt")))

    for caminho_mapa in caminhos:
        nome_mapa = caminho_mapa.stem
        mapa = ler_mapa(str(caminho_mapa))
        bonus_idx = numerar_bonus(mapa)

        g_pos = construir_grafo_posicoes(mapa)
        g_est, _inicio = construir_grafo_estados(mapa)

        # Métricas de G_pos
        v_pos = len(g_pos.retornar_vertices())
        e_pos = len(g_pos.retornar_ligacoes())
        d_pos = calcular_densidade(v_pos, e_pos)

        # Métricas de G_est (excluindo o nó virtual ALVO)
        vertices_est_reais = [v for v in g_est.retornar_vertices() if v != "ALVO"]
        arcos_est_reais = [
            (u, v, p) for u, v, p in g_est.retornar_ligacoes() if u != "ALVO" and v != "ALVO"
        ]
        v_est = len(vertices_est_reais)
        e_est = len(arcos_est_reais)
        d_est = calcular_densidade(v_est, e_est)

        # Teto teórico e taxa de ocupação
        qtd_chaves, qtd_bonus = contar_elementos_teto(mapa)
        teto_teorico = v_pos * (2 ** qtd_chaves) * (2 ** qtd_bonus)
        taxa_ocupacao = (v_est / teto_teorico) if teto_teorico > 0 else 0.0

        # Camadas (subgrafos induzidos) e arcos entre camadas
        metricas_camadas, info_transicoes = calcular_camadas_e_transicoes(g_est, mapa)

        metricas_global_todos[nome_mapa] = {
            "G_pos": {
                "ordem": v_pos,
                "tamanho": e_pos,
                "densidade": round(d_pos, 6),
            },
            "G_est": {
                "ordem": v_est,
                "tamanho": e_est,
                "densidade": round(d_est, 6),
            },
            "teto_teorico": teto_teorico,
            "taxa_ocupacao": round(taxa_ocupacao, 6),
            "arcos_entre_camadas": info_transicoes,
            "graus_e_rankings": calcular_graus_e_rankings(g_est, mapa, bonus_idx),
        }

        camadas_todos[nome_mapa] = metricas_camadas

        exportar_graus_csv(nome_mapa, g_est, bonus_idx, pasta_saida)
        exportar_arestas_csv(nome_mapa, g_est, bonus_idx, pasta_saida, mapa)

    exportar_saidas_caminhos_e_analises(caminhos, pasta_saida)
    exportar_bellman_ford_m05(pasta_saida)
    with open(pasta_saida / "metricas_global.json", mode="w", encoding="utf-8") as f:
        json.dump(metricas_global_todos, f, indent=4, ensure_ascii=False)

    with open(pasta_saida / "camadas.json", mode="w", encoding="utf-8") as f:
        json.dump(camadas_todos, f, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    gerar_relatorios()
    print("Arquivos das Seções 2 e 3 gerados em out/parte1/!")