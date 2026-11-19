import csv
import json
from pathlib import Path
from src.graphs.io import ler_mapa
from src.graphs.estados import construir_grafo_posicoes, construir_grafo_estados


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


def formatar_estado(estado: tuple) -> str:
    (i, j), chaves, bonus = estado
    chaves_str = "".join(sorted(chaves)) if chaves else "-"
    bonus_str = ";".join(f"{bi}:{bj}" for bi, bj in sorted(bonus)) if bonus else "-"
    return f"({i},{j})|chaves:{chaves_str}|bonus:{bonus_str}"


def calcular_camadas_e_transicoes(grafo_estados, mapa: list[str]) -> tuple[dict, dict]:
    vertices = grafo_estados.retornar_vertices()
    arcos = grafo_estados.retornar_ligacoes()

    # Agrupa vértices por conjunto de chaves (camadas)
    vertices_por_camada: dict[frozenset, set] = {}
    for v in vertices:
        chaves = v[1]
        vertices_por_camada.setdefault(chaves, set()).add(v)

    # Conta arcos internos de cada camada e arcos entre camadas diferentes
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
            pos_dest = destino[0]  # (i, j) da casa onde a chave foi coletada
            simbolo = mapa[pos_dest[0]][pos_dest[1]]
            casas_geradoras_transicao.add((pos_dest[0], pos_dest[1], simbolo))

    # Monta dicionário de métricas por camada (subgrafo induzido)
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

    # Ordena as casas que geram transição entre camadas
    casas_ordenadas = [
        {"linha": i, "coluna": j, "simbolo": simb}
        for i, j, simb in sorted(casas_geradoras_transicao)
    ]

    info_arcos_entre_camadas = {
        "quantidade_arcos": qtd_arcos_entre_camadas,
        "casas_geradoras": casas_ordenadas,
    }

    return metricas_camadas, info_arcos_entre_camadas


def exportar_graus_csv(nome_mapa: str, grafo_estados, pasta_saida: Path) -> None:
    vertices = grafo_estados.retornar_vertices()
    arcos = grafo_estados.retornar_ligacoes()

    grau_entrada = {v: 0 for v in vertices}
    grau_saida = {v: len(grafo_estados.retornar_vizinhos(v)) for v in vertices}

    for _origem, destino, _peso in arcos:
        grau_entrada[destino] += 1

    caminho_csv = pasta_saida / f"graus_{nome_mapa}.csv"
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["estado", "grau_entrada", "grau_saida"])
        for v in vertices:
            writer.writerow([formatar_estado(v), grau_entrada[v], grau_saida[v]])


def gerar_relatorios() -> None:
    pasta_mapas = Path("data/mapas")
    pasta_saida = Path("out/parte1")
    pasta_saida.mkdir(parents=True, exist_ok=True)

    metricas_global_todos = {}
    camadas_todos = {}

    for caminho_mapa in sorted(pasta_mapas.glob("*.txt")):
        nome_mapa = caminho_mapa.stem
        mapa = ler_mapa(str(caminho_mapa))

        g_pos = construir_grafo_posicoes(mapa)
        g_est, _inicio = construir_grafo_estados(mapa)

        # Métricas de G_pos
        v_pos = len(g_pos.retornar_vertices())
        e_pos = len(g_pos.retornar_ligacoes())
        d_pos = calcular_densidade(v_pos, e_pos)

        # Métricas de G_est
        v_est = len(g_est.retornar_vertices())
        e_est = len(g_est.retornar_ligacoes())
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
        }

        camadas_todos[nome_mapa] = metricas_camadas

        # Exporta graus_<mapa>.csv
        exportar_graus_csv(nome_mapa, g_est, pasta_saida)

    with open(pasta_saida / "metricas_global.json", mode="w", encoding="utf-8") as f:
        json.dump(metricas_global_todos, f, indent=4, ensure_ascii=False)

    with open(pasta_saida / "camadas.json", mode="w", encoding="utf-8") as f:
        json.dump(camadas_todos, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    gerar_relatorios()
    print("Arquivos da Seção 3 gerados em out/parte1/!")