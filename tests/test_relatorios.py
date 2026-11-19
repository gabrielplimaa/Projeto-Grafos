import csv
import json
from pathlib import Path
from src.graphs.main import gerar_relatorios


def test_saidas():
    pasta_saida = Path("out/parte1")
    arq_global = pasta_saida / "metricas_global.json"
    arq_camadas = pasta_saida / "camadas.json"

    gerar_relatorios()

    assert arq_global.exists()
    assert arq_camadas.exists()

    with open(arq_global, encoding="utf-8") as f:
        dados_global = json.load(f)

    assert len(dados_global) > 0

    for nome_mapa, info in dados_global.items():
        assert "G_pos" in info and "G_est" in info
        assert "teto_teorico" in info and "taxa_ocupacao" in info

        arq_csv = pasta_saida / f"graus_{nome_mapa}.csv"
        assert arq_csv.exists()

        with open(arq_csv, encoding="utf-8") as f_csv:
            leitor = list(csv.reader(f_csv))
            assert leitor[0] == ["estado", "grau_entrada", "grau_saida"]
            assert len(leitor) - 1 == info["G_est"]["ordem"]