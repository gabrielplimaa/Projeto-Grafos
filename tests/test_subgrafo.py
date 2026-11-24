import pandas as pd
import pytest
from src.graphs.graph import gerar_subgrafo_amostra, construir_grafo_de_dataframe


@pytest.fixture
def df_exemplo():
    return pd.DataFrame({
        "source": [1, 1, 2, 3, 4, 5],
        "target": [2, 3, 4, 4, 5, 1],
        "peso": [1.0, 2.5, 1.5, 3.0, 2.0, 4.0],
    })


def test_reprodutibilidade_seed(df_exemplo):
    amostra_1 = gerar_subgrafo_amostra(df_exemplo, fracao=0.60, seed=42)
    amostra_2 = gerar_subgrafo_amostra(df_exemplo, fracao=0.60, seed=42)
    pd.testing.assert_frame_equal(amostra_1, amostra_2)


def test_subgrafo_induzido_valido(df_exemplo):
    amostra = gerar_subgrafo_amostra(df_exemplo, fracao=0.60, seed=42)
    nos_no_df = set(amostra["source"]).union(set(amostra["target"]))

    assert amostra["source"].isin(nos_no_df).all()
    assert amostra["target"].isin(nos_no_df).all()


def test_fracao_invalida(df_exemplo):
    with pytest.raises(ValueError):
        gerar_subgrafo_amostra(df_exemplo, fracao=0.0)
    with pytest.raises(ValueError):
        gerar_subgrafo_amostra(df_exemplo, fracao=1.5)


def test_construcao_grafo_dataframe(df_exemplo):
    grafo = construir_grafo_de_dataframe(df_exemplo)
    nos_esperados = set(df_exemplo["source"]).union(set(df_exemplo["target"]))

    assert set(grafo.retornar_vertices()) == nos_esperados
    assert len(grafo.retornar_ligacoes()) == len(df_exemplo)