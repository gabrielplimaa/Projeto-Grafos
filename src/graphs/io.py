import gzip
import shutil
import urllib.request
from pathlib import Path
import pandas as pd
import random

from src.graphs.graph import Grafo

SIMBOLOS_VALIDOS = set("#.SG,~abcdABCD><^v+*")

URL_BITCOIN_OTC = "https://snap.stanford.edu/data/soc-sign-bitcoin-otc.csv.gz"
CAMINHO_PADRAO_CSV = Path("data/dataset_parte2/soc-sign-bitcoin-otc.csv")

def baixar_dataset_otc(caminho_csv=CAMINHO_PADRAO_CSV, url=URL_BITCOIN_OTC):
    caminho_csv = Path(caminho_csv)

    if caminho_csv.exists():
        return caminho_csv

    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    caminho_gz = caminho_csv.with_suffix(".csv.gz")

    try:
        urllib.request.urlretrieve(url, caminho_gz)

        with gzip.open(caminho_gz, "rb") as f_in, open(caminho_csv, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    finally:
        if caminho_gz.exists():
            caminho_gz.unlink()

    return caminho_csv

def carregar_dataframe_otc(caminho_csv=CAMINHO_PADRAO_CSV):
    caminho_csv = baixar_dataset_otc(caminho_csv)
    df = pd.read_csv(caminho_csv, header=None, names=["source", "target", "rating", "time"])

    stats = {
        "linhas_originais": len(df),
        "nulos": {k: int(v) for k, v in df.isna().sum().to_dict().items()},
    }

    df = df.dropna().copy()

    stats["auto_lacos"] = int((df["source"] == df["target"]).sum())
    df = df[df["source"] != df["target"]].copy()

    stats["duplicadas"] = int(df.duplicated(subset=["source", "target"]).sum())
    df = df.sort_values("time", ascending=True).drop_duplicates(subset=["source", "target"], keep="last")

    df["source"] = df["source"].astype(str)
    df["target"] = df["target"].astype(str)
    df["peso_bf"] = -df["rating"]
    df["peso_dijkstra"] = 11 - df["rating"]
    df["datetime"] = pd.to_datetime(df["time"], unit="s")

    df = df.reset_index(drop=True)
    stats["linhas_finais"] = len(df)

    return df, stats

def construir_grafo_otc(df, coluna_peso="peso_bf", fracao_nos=1.0, seed=42):
    if fracao_nos < 1.0:
        nos_unicos = sorted(set(df["source"]).union(df["target"]))
        k = int(len(nos_unicos) * fracao_nos)
        nos_amostra = set(random.Random(seed).sample(nos_unicos, k))
        df = df[df["source"].isin(nos_amostra) & df["target"].isin(nos_amostra)]

    g = Grafo()
    nos_presentes = set(df["source"]).union(df["target"])
    for no in nos_presentes:
        g.adicionar_no(no)

    for u, v, peso in zip(df["source"], df["target"], df[coluna_peso]):
        g.ligar(u, v, float(peso))

    return g

def ler_mapa(caminho):
    linhas = []
    with open(caminho, "r", encoding="utf-8") as file:
        for linha in file:
            if linha.lstrip().startswith(";"):
                continue
            linhas.append(linha.rstrip("\r\n"))

    # Remove linhas em branco apenas no final do arquivo
    while linhas and linhas[-1].strip() == "":
        linhas.pop()

    if len(linhas) == 0:
        raise ValueError("Mapa vazio")

    qtd = len(linhas[0])
    qtd_s = 0
    qtd_g = 0

    for linha in linhas:
        if len(linha) != qtd:
            raise ValueError("Mapa não retangular")
        for c in linha:
            if c not in SIMBOLOS_VALIDOS:
                raise ValueError(f"Símbolo inválido no mapa: {c!r}")
            if c == "S":
                qtd_s += 1
            elif c == "G":
                qtd_g += 1

    if qtd_s != 1:
        raise ValueError(f"O mapa deve ter exatamente um início 'S' (encontrados: {qtd_s})")
    if qtd_g < 1:
        raise ValueError("O mapa deve ter pelo menos uma saída 'G'")

    return linhas