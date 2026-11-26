"""Gera os 7 gráficos da Parte 2 (rede com pesos negativos) usando apenas matplotlib, pandas, numpy e networkx."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def _estilizar_eixo(ax):
    ax.set_axisbelow(True)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _carregar_dataset_parte2(caminho_dataset):
    df = pd.read_csv(caminho_dataset, header=None)
    if not np.issubdtype(df.iloc[:, 2].dtype, np.number):
        df = pd.read_csv(caminho_dataset)

    df = df.iloc[:, :3].copy()
    df.columns = ["origem", "destino", "rating"]
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["origem", "destino", "rating"])
    df["origem"] = df["origem"].astype(str)
    df["destino"] = df["destino"].astype(str)
    return df


def _montar_atributos_nos(df):
    out_stats = df.groupby("origem")["rating"].agg(
        grau_saida="count",
        media_emitido="mean",
        positivos_emitidos=lambda s: (s > 0).sum(),
        negativos_emitidos=lambda s: (s < 0).sum(),
    )
    in_stats = df.groupby("destino")["rating"].agg(
        grau_entrada="count",
        media_recebido="mean",
        saldo_liquido="sum",
        positivos_recebidos=lambda s: (s > 0).sum(),
        negativos_recebidos=lambda s: (s < 0).sum(),
    )

    nos = out_stats.join(in_stats, how="outer").fillna(
        {
            "grau_saida": 0,
            "grau_entrada": 0,
            "positivos_emitidos": 0,
            "negativos_emitidos": 0,
            "saldo_liquido": 0,
            "positivos_recebidos": 0,
            "negativos_recebidos": 0,
        }
    )
    nos["grau_total"] = nos["grau_entrada"] + nos["grau_saida"]
    nos["grau_positivo"] = nos["positivos_emitidos"] + nos["positivos_recebidos"]
    nos["grau_negativo"] = nos["negativos_emitidos"] + nos["negativos_recebidos"]
    nos["taxa_negativa_emitida"] = np.where(
        nos["grau_saida"] > 0,
        nos["negativos_emitidos"] / nos["grau_saida"],
        0.0,
    )
    nos["taxa_negativa_recebida"] = np.where(
        nos["grau_entrada"] > 0,
        nos["negativos_recebidos"] / nos["grau_entrada"],
        0.0,
    )

    G = nx.DiGraph()
    G.add_edges_from(zip(df["origem"], df["destino"]))
    pr = nx.pagerank(G)
    nos["pagerank"] = nos.index.map(pr).fillna(0.0)

    return nos


def _plot_01_distribuicao_ratings(df, pasta_out):
    contagem = df["rating"].value_counts().sort_index()
    valores = contagem.index.to_numpy()
    freqs = contagem.to_numpy()
    cores = ["#c53030" if v < 0 else "#2b6cb0" for v in valores]

    pct_pos = (df["rating"] > 0).mean() * 100
    pct_neg = (df["rating"] < 0).mean() * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(valores, freqs, color=cores, edgecolor="white", width=0.8)

    # Destaca os maiores picos
    top_indices = np.argsort(freqs)[-4:]
    for idx in top_indices:
        b = barras[idx]
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + freqs.max() * 0.015,
            f"{int(freqs[idx])}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
        )

    ax.axvline(0, color="#4a5568", linestyle="--", linewidth=1.2)
    ax.bar([], [], color="#2b6cb0", label=f"Positivos ({pct_pos:.1f}%)")
    ax.bar([], [], color="#c53030", label=f"Negativos ({pct_neg:.1f}%)")

    ax.set_title("Distribuição das Avaliações (Ratings)", fontweight="bold")
    ax.set_xlabel("Rating (Peso da Aresta)")
    ax.set_ylabel("Frequência (Nº de Arestas)")
    ax.legend()
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "01_distribuicao_ratings.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_02_distribuicao_graus_loglog(nos, pasta_out):
    # [IA] Claude Code – eixos x e y em escala log (gráfico log-log)
    pos_counts = nos.loc[nos["grau_positivo"] > 0, "grau_positivo"].value_counts().sort_index()
    neg_counts = nos.loc[nos["grau_negativo"] > 0, "grau_negativo"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.scatter(
        pos_counts.index,
        pos_counts.values,
        color="#2b6cb0",
        alpha=0.75,
        s=32,
        label="Grau Positivo (rating > 0)",
    )
    ax.scatter(
        neg_counts.index,
        neg_counts.values,
        color="#c53030",
        alpha=0.75,
        s=32,
        marker="^",
        label="Grau Negativo (rating < 0)",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Distribuição de Graus Positivos vs. Negativos", fontweight="bold")
    ax.set_xlabel("Grau (k)")
    ax.set_ylabel("Frequência (Nº de Nós)")
    ax.legend()
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "02_distribuicao_graus_loglog.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_03_correlacao_spearman(nos, pasta_out):
    cols = {
        "grau_entrada": "Grau Entrada",
        "grau_saida": "Grau Saída",
        "pagerank": "PageRank",
        "saldo_liquido": "Saldo Líquido",
        "taxa_negativa_recebida": "Taxa Neg. Recebida",
    }
    corr = nos[list(cols.keys())].rename(columns=cols).corr(method="spearman")

    fig, ax = plt.subplots(figsize=(7.8, 6.4))
    im = ax.imshow(corr.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)

    labels = list(corr.columns)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr.iloc[i, j]
            cor_texto = "white" if abs(val) > 0.55 else "#1a202c"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=cor_texto, fontweight="bold")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Correlação de Spearman (ρ)")
    ax.set_title("Correlação de Spearman — Topologia vs. Reputação", fontweight="bold", pad=14)
    plt.tight_layout()

    saida = pasta_out / "03_correlacao_spearman_atributos.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_04_boxplot_outliers_emissao(nos, pasta_out):
    pos_rec = nos.loc[nos["positivos_recebidos"] > 0, "positivos_recebidos"].to_numpy()
    neg_rec = nos.loc[nos["negativos_recebidos"] > 0, "negativos_recebidos"].to_numpy()

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bp = ax.boxplot(
        [pos_rec, neg_rec],
        tick_labels=["Avaliações Positivas\nRecebidas", "Avaliações Negativas\nRecebidas"],
        vert=False,
        patch_artist=True,
        flierprops={
            "marker": "o",
            "markersize": 4,
            "alpha": 0.45,
            "markerfacecolor": "#c53030",
            "markeredgecolor": "none",
        },
    )

    for patch, cor in zip(bp["boxes"], ["#2b6cb0", "#c53030"]):
        patch.set_facecolor(cor)
        patch.set_alpha(0.65)
    for median in bp["medians"]:
        median.set_color("#1a202c")
        median.set_linewidth(2)

    ax.set_title("Outliers de Avaliações Positivas e Negativas Recebidas", fontweight="bold")
    ax.set_xlabel("Quantidade de Avaliações Recebidas")
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "04_boxplot_outliers_emissao.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_05_curva_lorenz_gini(nos, pasta_out):
    valores = np.sort(nos.loc[nos["grau_saida"] > 0, "grau_saida"].to_numpy())
    n = len(valores)
    acumulado_y = np.concatenate([[0], np.cumsum(valores) / np.sum(valores)])
    acumulado_x = np.linspace(0, 1, n + 1)

    area_lorenz = np.trapezoid(acumulado_y, acumulado_x)
    gini = 1.0 - 2.0 * area_lorenz

    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.plot([0, 1], [0, 1], linestyle="--", color="#718096", linewidth=1.6, label="Igualdade Perfeita")
    ax.plot(acumulado_x, acumulado_y, color="#2b6cb0", linewidth=2.4, label=f"Curva de Lorenz (Gini = {gini:.3f})")
    ax.fill_between(acumulado_x, acumulado_y, acumulado_x, color="#2b6cb0", alpha=0.15)

    ax.set_title(f"Curva de Lorenz — Desigualdade na Emissão (Gini = {gini:.3f})", fontweight="bold")
    ax.set_xlabel("Fração Acumulada de Emissores")
    ax.set_ylabel("Fração Acumulada de Avaliações Emitidas")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="upper left")
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "05_curva_lorenz_gini_emissao.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_06_top_emissores_vs_volume(nos, pasta_out, top_n=15):
    top = nos.sort_values("grau_saida", ascending=False).head(top_n).iloc[::-1]
    y = np.arange(len(top))
    pos = top["positivos_emitidos"].to_numpy()
    neg = top["negativos_emitidos"].to_numpy()

    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.barh(y, pos, color="#2b6cb0", label="Avaliações Positivas")
    ax.barh(y, neg, left=pos, color="#c53030", label="Avaliações Negativas")

    for i, (p, n) in enumerate(zip(pos, neg)):
        total = int(p + n)
        ax.text(total + max(pos + neg) * 0.01, i, f"{total}", va="center", fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels([f"Nó {idx}" for idx in top.index])
    ax.set_title(f"Top {top_n} Emissores vs. Volume de Avaliações", fontweight="bold")
    ax.set_xlabel("Volume de Avaliações Emitidas")
    ax.set_ylabel("Usuário (ID)")
    ax.legend(loc="lower right")
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "06_top_emissores_vs_volume.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def _plot_07_comparacao_algoritmos_parte2(pasta_out, caminho_report=Path("out/parte2/parte2_report.json")):
    # [IA] Claude Code – plota tempos dos algoritmos do grupo lidos do parte2_report.json
    with open(caminho_report, encoding="utf-8") as f:
        report = json.load(f)
    execucoes = sorted(report["escalabilidade_5_execucoes"], key=lambda e: e["fracao_nos"])

    rotulos_x = [f"{e['fracao_nos']:.0%}\n(|V| = {e['ordem_V']})" for e in execucoes]
    x = np.arange(len(execucoes))

    series = [
        ("BFS", "BFS — O(V + E)", "o", "#2b6cb0"),
        ("DFS", "DFS — O(V + E)", "D", "#805ad5"),
        ("Dijkstra", "Dijkstra — O((V + E) log V)", "s", "#2f855a"),
        ("Bellman_Ford", "Bellman-Ford — O(V · E)", "^", "#c53030"),
    ]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for chave, rotulo, marcador, cor in series:
        tempos_ms = [e["tempo_medio_s"][chave] * 1000.0 for e in execucoes]
        ax.plot(x, tempos_ms, marker=marcador, linewidth=2.2, color=cor, label=rotulo)

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos_x)
    ax.set_title("Escalabilidade dos Algoritmos do Grupo — Parte 2", fontweight="bold")
    ax.set_xlabel("Tamanho do subgrafo (fração dos nós do Bitcoin OTC)")
    ax.set_ylabel("Tempo médio de 5 execuções (ms, escala log)")
    ax.legend()
    _estilizar_eixo(ax)
    plt.tight_layout()

    saida = pasta_out / "07_comparacao_algoritmos_parte2.png"
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    return saida


def gerar_graficos_relatorio(pasta_saida, caminho_dataset=None, repeticoes=3):
    if caminho_dataset is None:
        raise ValueError("Informe o dataset da Parte 2 com --dataset caminho/do/arquivo.csv")

    pasta_out = Path(pasta_saida)
    pasta_out.mkdir(parents=True, exist_ok=True)

    df = _carregar_dataset_parte2(caminho_dataset)
    nos = _montar_atributos_nos(df)



    return [
        _plot_01_distribuicao_ratings(df, pasta_out),
        _plot_02_distribuicao_graus_loglog(nos, pasta_out),
        _plot_03_correlacao_spearman(nos, pasta_out),
        _plot_04_boxplot_outliers_emissao(nos, pasta_out),
        _plot_05_curva_lorenz_gini(nos, pasta_out),
        _plot_06_top_emissores_vs_volume(nos, pasta_out),
        _plot_07_comparacao_algoritmos_parte2(pasta_out),
    ]