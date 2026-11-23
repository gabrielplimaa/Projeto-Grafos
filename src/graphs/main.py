import csv
import json
from pathlib import Path
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


def exportar_arestas_csv(nome_mapa: str, grafo_estados, bonus_idx: dict, pasta_saida: Path) -> None:
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
                f"({dest_i},{dest_j})",
                peso,
            ])


def gerar_relatorios() -> None:
    pastas_mapas = [Path("data/mapas"), Path("data/mapas_grupo")]
    pasta_saida = Path("out/parte1")
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
        }

        camadas_todos[nome_mapa] = metricas_camadas

        exportar_graus_csv(nome_mapa, g_est, bonus_idx, pasta_saida)
        exportar_arestas_csv(nome_mapa, g_est, bonus_idx, pasta_saida)

    with open(pasta_saida / "metricas_global.json", mode="w", encoding="utf-8") as f:
        json.dump(metricas_global_todos, f, indent=4, ensure_ascii=False)

    with open(pasta_saida / "camadas.json", mode="w", encoding="utf-8") as f:
        json.dump(camadas_todos, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    gerar_relatorios()
    print("Arquivos das Seções 2 e 3 gerados em out/parte1/!")