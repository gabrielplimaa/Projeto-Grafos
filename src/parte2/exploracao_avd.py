# [IA] Gemini – apoio com sintaxe de pandas para diagnóstico dos 4 pilares de AVD no Bitcoin OTC.
import pandas as pd
from pathlib import Path

ARQUIVO = Path("data/dataset_parte2/soc-sign-bitcoinotc.csv")
df = pd.read_csv(ARQUIVO, names=["source", "target", "rating", "time"])
df["data_utc"] = pd.to_datetime(df["time"], unit="s", utc=True)

print("=== 1. PILAR ESTRUTURAL (DADOS & GRAFOS) ===")
print(f"Total de registros (arestas): {len(df)} | Colunas: {list(df.columns)}")
print("\nTipos de dados:")
print(df.dtypes)
print("\nValores ausentes (NaN) por coluna:")
print(df.isna().sum().to_dict())
print(f"Linhas duplicadas exatas: {df.duplicated().sum()}")
print(f"Auto-laços (source == target): {(df['source'] == df['target']).sum()}")
print(f"Pares (source, target) duplicados: {df.duplicated(subset=['source', 'target']).sum()}")

nos = set(df["source"]).union(set(df["target"]))
V, E = len(nos), len(df)
densidade = E / (V * (V - 1))
print(f"Grafo -> |V| = {V} | |E| = {E} | Densidade dirigida = {densidade:.6f}")
print(f"Período temporal: {df['data_utc'].min()} até {df['data_utc'].max()}")

print("\n=== 2. PILAR DISTRIBUCIONAL ===")
print("Resumo estatístico de 'rating':")
print(df["rating"].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))
neg = (df["rating"] < 0).sum()
pos = (df["rating"] > 0).sum()
print(f"Negativos (< 0): {neg} ({neg/E*100:.2f}%) | Positivos (> 0): {pos} ({pos/E*100:.2f}%)")

grau_saida = df.groupby("source").size()
grau_entrada = df.groupby("target").size()
print("\nGrau de saída (descrição):", grau_saida.describe().to_dict())
print("Grau de entrada (descrição):", grau_entrada.describe().to_dict())

print("\n=== 3. PILAR RELACIONAL (MULTIVARIADO) ===")
perfil = pd.DataFrame({
    "grau_entrada": grau_entrada,
    "grau_saida": grau_saida,
    "rating_medio_recebido": df.groupby("target")["rating"].mean(),
    "rating_medio_enviado": df.groupby("source")["rating"].mean(),
    "prop_negativas_recebidas": df.groupby("target")["rating"].apply(lambda s: (s < 0).mean()),
}).fillna(0)
print("Correlação de Spearman entre atributos dos nós:")
print(perfil.corr(method="spearman").round(4))

print("\n=== 4. DETECÇÃO DE OUTLIERS (IQR) ===")
for nome, serie in [("Rating", df["rating"]), ("Grau Entrada", grau_entrada), ("Grau Saída", grau_saida)]:
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    outliers = serie[(serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)]
    print(f"{nome}: Q1={q1}, Q3={q3}, IQR={iqr} -> Outliers={len(outliers)} ({len(outliers)/len(serie)*100:.2f}%)")