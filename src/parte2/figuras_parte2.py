# [IA] Gemini – apoio com sintaxe de matplotlib/numpy/pandas para geração das 7 figuras da Parte 2 e AVD.
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ARQUIVO_CSV = Path("data/dataset_parte2/soc-sign-bitcoinotc.csv")
ARQUIVO_JSON = Path("out/parte2/parte2_report.json")
PASTA_SAIDA = Path("out/parte2")


def _gini(valores):
    arr = np.sort(np.asarray(valores, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    indices = np.arange(1, n + 1)
    return float((2 * np.sum(indices * arr) / (n * np.sum(arr))) - (n + 1) / n)


def _curva_lorenz(valores):
    arr = np.sort(np.asarray(valores, dtype=float))
    soma_acum = np.cumsum(arr) / arr.sum()
    x = np.insert(np.arange(1, len(arr) + 1) / len(arr), 0, 0.0)
    y = np.insert(soma_acum, 0, 0.0)
    return x, y


def _fatia_top(valores, pct):
    arr = np.sort(np.asarray(valores, dtype=float))[::-1]
    k = max(1, int(np.ceil(len(arr) * pct)))
    return float(arr[:k].sum() / arr.sum() * 100.0), k


def gerar_todas_figuras():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    })

    df = pd.read_csv(ARQUIVO_CSV, names=["source", "target", "rating", "time"])
    with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
        rep = json.load(f)

    # =========================================================================
    # FIGURA 01 (Exploratória 1): Distribuição das Notas (-10 a +10)
    # =========================================================================
    notas = list(range(-10, 11))
    contagens = df["rating"].value_counts().reindex(notas, fill_value=0)
    pcts = contagens / len(df) * 100.0
    cores = ["#c0392b" if n < 0 else ("#7f8c8d" if n == 0 else "#2980b9") for n in notas]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    barras = ax.bar([str(n) for n in notas], contagens.values, color=cores, edgecolor="none")
    ax.set_title("Distribuição das Avaliações de Confiança no Bitcoin OTC (N = 35.592)", fontweight="bold")
    ax.set_xlabel("Nota atribuída (rating)")
    ax.set_ylabel("Número de avaliações")
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for idx in [0, 11, 20]:  # -10, +1, +10
        b = barras[idx]
        ax.annotate(
            f"{contagens.iloc[idx]:,}\n({pcts.iloc[idx]:.1f}%)",
            xy=(b.get_x() + b.get_width() / 2, b.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            fontweight="bold",
        )
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "01_distribuicao_ratings.png")
    plt.close(fig)

    # =========================================================================
    # FIGURA 02 (Exploratória 2): Distribuição de Graus (Entrada e Saída, Log-Log)
    # =========================================================================
    g_out = df.groupby("source").size()
    g_in = df.groupby("target").size()

    fig, ax = plt.subplots(figsize=(8.5, 5))
    for serie, rotulo, cor, marker in [
        (g_out, "Grau de saída (avaliações enviadas)", "#1f77b4", "o"),
        (g_in, "Grau de entrada (avaliações recebidas)", "#d95f02", "s"),
    ]:
        freq = serie.value_counts().sort_index()
        ax.scatter(freq.index, freq.values, label=rotulo, color=cor, marker=marker, alpha=0.75, s=28)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Distribuição de Graus da Rede Dirigida (Escala Log-Log)", fontweight="bold")
    ax.set_xlabel("Grau k (escala log)")
    ax.set_ylabel("Frequência de nós com grau k (escala log)")
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "02_distribuicao_graus_loglog.png")
    plt.close(fig)

    # =========================================================================
    # FIGURA 03 (Exploratória 3): Matriz de Correlação de Spearman
    # =========================================================================
    perfil = pd.DataFrame({
        "Grau Entrada": g_in,
        "Grau Saída": g_out,
        "Média Recebida": df.groupby("target")["rating"].mean(),
        "Média Enviada": df.groupby("source")["rating"].mean(),
        "% Negativas Recebidas": df.groupby("target")["rating"].apply(lambda s: (s < 0).mean() * 100),
    }).fillna(0)
    corr = perfil.corr(method="spearman")

    fig, ax = plt.subplots(figsize=(7.5, 6))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=30, ha="right")
    ax.set_yticklabels(corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            val = corr.iloc[i, j]
            cor_txt = "white" if abs(val) > 0.55 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=cor_txt, fontsize=9.5, fontweight="bold")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Correlação de Spearman (ρ)")
    ax.set_title("Pilar Relacional: Correlação de Spearman entre Atributos dos Nós", fontweight="bold")
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "03_correlacao_spearman_atributos.png")
    plt.close(fig)

    # =========================================================================
    # FIGURA 04 (Exploratória 4): Boxplots de Outliers (IQR) na Emissão por Usuário
    # =========================================================================
    emissoes_totais = df.groupby("source").size()
    emissoes_mais1 = df[df["rating"] == 1].groupby("source").size()
    emissoes_menos10 = df[df["rating"] == -10].groupby("source").size()

    fig, ax = plt.subplots(figsize=(8.5, 5))
    dados_box = [emissoes_totais.values, emissoes_mais1.values, emissoes_menos10.values]
    rotulos_box = [
        f"Total Emitido\n(n={len(emissoes_totais)})",
        f"Notas +1 Emitidas\n(n={len(emissoes_mais1)})",
        f"Notas -10 Emitidas\n(n={len(emissoes_menos10)})",
    ]
    bp = ax.boxplot(dados_box, tick_labels=rotulos_box, patch_artist=True, showfliers=True,
                    flierprops=dict(marker="o", markersize=4, alpha=0.45, markeredgecolor="#555555"))
    for patch, cor in zip(bp["boxes"], ["#5dade2", "#2980b9", "#c0392b"]):
        patch.set_facecolor(cor)
        patch.set_alpha(0.75)

    ax.set_yscale("log")
    ax.set_ylabel("Quantidade de avaliações emitidas por usuário (escala log)")
    ax.set_title("Detecção de Outliers (IQR) no Volume de Emissão por Usuário", fontweight="bold")
    ax.grid(axis="y", which="both", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "04_boxplot_outliers_emissao.png")
    plt.close(fig)

    # =========================================================================
    # FIGURA 05 (Explanatória 1): Curva de Lorenz e Índice de Gini (+1 vs -10)
    # =========================================================================
    x_m1, y_m1 = _curva_lorenz(emissoes_mais1.values)
    x_m10, y_m10 = _curva_lorenz(emissoes_menos10.values)
    x_tot, y_tot = _curva_lorenz(emissoes_totais.values)

    gini_m1 = _gini(emissoes_mais1.values)
    gini_m10 = _gini(emissoes_menos10.values)
    gini_tot = _gini(emissoes_totais.values)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="#7f8c8d", label="Igualdade perfeita (Gini = 0,00)")
    ax.plot(x_tot, y_tot, color="#34495e", linewidth=1.8, linestyle=":",
            label=f"Todas as avaliações (Gini = {gini_tot:.3f})")
    ax.plot(x_m1, y_m1, color="#2980b9", linewidth=2.4,
            label=f"Avaliações +1 (Gini = {gini_m1:.3f} | {len(emissoes_mais1)} emissores)")
    ax.plot(x_m10, y_m10, color="#c0392b", linewidth=2.4,
            label=f"Avaliações -10 (Gini = {gini_m10:.3f} | {len(emissoes_menos10)} emissores)")

    # Destaca o ponto dos Top 10% mais ativos (x = 0.90)
    for x_arr, y_arr, cor in [(x_m1, y_m1, "#2980b9"), (x_m10, y_m10, "#c0392b")]:
        y_90 = float(np.interp(0.90, x_arr, y_arr))
        top10_share = (1.0 - y_90) * 100.0
        ax.scatter([0.90], [y_90], color=cor, zorder=5)
        ax.annotate(f"Top 10% concentram\n{top10_share:.1f}% das notas",
                    xy=(0.90, y_90), xytext=(0.56, y_90 - 0.08 if cor == "#2980b9" else y_90 + 0.05),
                    arrowprops=dict(arrowstyle="->", color=cor, lw=1.1),
                    fontsize=8.5, fontweight="bold", color=cor)

    ax.set_title("Curva de Lorenz: Concentração da Emissão de +1 vs. -10 entre Emissores", fontweight="bold")
    ax.set_xlabel("Fração acumulada de usuários emissores (do menor ao maior)")
    ax.set_ylabel("Fração acumulada de avaliações emitidas")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "05_curva_lorenz_gini_emissao.png")
    plt.close(fig)

    # =========================================================================
    # FIGURA 06 (Explanatória 2): Top 15 Emissores de +1 e -10
    # =========================================================================
    top15_m1 = emissoes_mais1.sort_values(ascending=False).head(15)[::-1]
    top15_m10 = emissoes_menos10.sort_values(ascending=False).head(15)[::-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))

    b1 = ax1.barh([f"Nó {u}" for u in top15_m1.index], top15_m1.values, color="#2980b9")
    ax1.set_title(f"Top 15 Emissores de +1 ({top15_m1.sum()/emissoes_mais1.sum()*100:.1f}% do total de +1)",
                  fontweight="bold", fontsize=10)
    ax1.set_xlabel("Quantidade de notas +1 emitidas")
    ax1.grid(axis="x", linestyle="--", alpha=0.35)
    for bar in b1:
        ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                 f"{int(bar.get_width())}", va="center", fontsize=8.5)
    ax1.set_xlim(0, top15_m1.max() * 1.15)

    b2 = ax2.barh([f"Nó {u}" for u in top15_m10.index], top15_m10.values, color="#c0392b")
    ax2.set_title(f"Top 15 Emissores de -10 ({top15_m10.sum()/emissoes_menos10.sum()*100:.1f}% do total de -10)",
                  fontweight="bold", fontsize=10)
    ax2.set_xlabel("Quantidade de notas -10 emitidas")
    ax2.grid(axis="x", linestyle="--", alpha=0.35)
    for bar in b2:
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                 f"{int(bar.get_width())}", va="center", fontsize=8.5)
    ax2.set_xlim(0, top15_m10.max() * 1.15)

    fig.suptitle("Quem Concentra as Avaliações Extremas? Ranking dos Maiores Emissores", fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "06_top_emissores_vs_volume.png", bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # FIGURA 07 (Grafos - Parte 2): Escalabilidade e Estrutura de Arcos (DFS)
    # =========================================================================
    esc = rep["escalabilidade_5_execucoes"]
    escalas_lbl = [f"{int(e['fracao_nos']*100)}%\n(|V|={e['ordem_V']})" for e in esc]
    x_esc = np.arange(len(esc))

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 4.8))

    for alg, rotulo, cor, mk in [
        ("BFS", "BFS — O(|V| + |E|)", "#27ae60", "o"),
        ("DFS", "DFS — O(|V| + |E|)", "#2980b9", "s"),
        ("Dijkstra", "Dijkstra — O((|V|+|E|) log |V|)", "#f39c12", "^"),
        ("Bellman_Ford", "Bellman-Ford — O(|V|·|E|)", "#c0392b", "D"),
    ]:
        tempos = [e["tempo_medio_s"][alg] for e in esc]
        ax_a.plot(x_esc, tempos, marker=mk, linewidth=2.2, color=cor, label=rotulo)

    ax_a.set_xticks(x_esc)
    ax_a.set_xticklabels(escalas_lbl)
    ax_a.set_yscale("log")
    ax_a.set_ylabel("Tempo médio de 5 execuções (s, escala log)")
    ax_a.set_title("Escalabilidade Empírica dos Algoritmos", fontweight="bold")
    ax_a.grid(True, which="both", linestyle="--", alpha=0.35)
    ax_a.legend(fontsize=8.5)

    dfs_f0 = rep["dfs_3_fontes"][0]
    tipos_arco = ["Árvore", "Retorno", "Avanço", "Cruzamento"]
    vals_arco = [
        dfs_f0["contagens_arcos"]["arvore"],
        dfs_f0["contagens_arcos"]["retorno"],
        dfs_f0["contagens_arcos"]["avanco"],
        dfs_f0["contagens_arcos"]["cruzamento"],
    ]
    barras_dfs = ax_b.bar(tipos_arco, vals_arco, color=["#2980b9", "#c0392b", "#8e44ad", "#16a085"])
    ax_b.set_title(f"Classificação Estrutural de Arcos na DFS (Fonte = Nó {dfs_f0['fonte']})", fontweight="bold")
    ax_b.set_ylabel("Quantidade de arcos")
    ax_b.grid(axis="y", linestyle="--", alpha=0.35)
    for b in barras_dfs:
        ax_b.text(b.get_x() + b.get_width() / 2, b.get_height() + 250,
                  f"{int(b.get_height()):,}", ha="center", fontsize=9, fontweight="bold")
    ax_b.set_ylim(0, max(vals_arco) * 1.15)

    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / "07_comparacao_algoritmos_parte2.png")
    plt.close(fig)

    # =========================================================================
    # IMPRIME RESUMO QUANTITATIVO PARA O PDF AUTORAL
    # =========================================================================
    print("=== MÉTRICAS EXATAS DA PERGUNTA DE PESQUISA (+1 vs -10) ===")
    for nome, s, g in [
        ("Todas as notas", emissoes_totais, gini_tot),
        ("Notas +1", emissoes_mais1, gini_m1),
        ("Notas -10", emissoes_menos10, gini_m10),
    ]:
        t1, k1 = _fatia_top(s.values, 0.01)
        t5, k5 = _fatia_top(s.values, 0.05)
        t10, k10 = _fatia_top(s.values, 0.10)
        q1, med, q3 = s.quantile(0.25), s.median(), s.quantile(0.75)
        print(f"\n[{nome}] Total={int(s.sum())} | Emissores únicos={len(s)} | Gini={g:.4f}")
        print(f"  Mediana={med:.1f} | Q1={q1:.1f} | Q3={q3:.1f} | IQR={q3-q1:.1f} | Máx={s.max()}")
        print(f"  Top 1% ({k1} nós): {t1:.2f}% | Top 5% ({k5} nós): {t5:.2f}% | Top 10% ({k10} nós): {t10:.2f}%")

    print(f"\nTodas as 7 figuras salvas com sucesso em: {PASTA_SAIDA.resolve()}")


if __name__ == "__main__":
    gerar_todas_figuras()