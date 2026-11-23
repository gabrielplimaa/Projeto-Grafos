import pytest
from src.graphs.io import ler_mapa


def test_ler_mapa_valido(tmp_path):
    arquivo = tmp_path / "valido.txt"
    arquivo.write_text(
        "; comentario do mapa\n"
        "#####\n"
        "#S.G#\n"
        "#####\n"
        "\n",
        encoding="utf-8",
    )
    mapa = ler_mapa(arquivo)
    assert len(mapa) == 3
    assert mapa[1] == "#S.G#"


def test_ler_mapa_vazio(tmp_path):
    arquivo = tmp_path / "vazio.txt"
    arquivo.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        ler_mapa(str(arquivo))


def test_ler_mapa_nao_retangular(tmp_path):
    arquivo = tmp_path / "nao_retangular.txt"
    arquivo.write_text(
        "#####\n"
        "#S.G\n"
        "#####\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
            ler_mapa(str(arquivo))
    


def test_ler_mapa_dois_inicios(tmp_path):
    arquivo = tmp_path / "dois_s.txt"
    arquivo.write_text(
        "######\n"
        "#S.SG#\n"
        "######\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        ler_mapa(str(arquivo))


def test_ler_mapa_sem_saida(tmp_path):
    arquivo = tmp_path / "sem_g.txt"
    arquivo.write_text(
        "#####\n"
        "#S..#\n"
        "#####\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        ler_mapa(str(arquivo))


def test_ler_mapa_simbolo_invalido(tmp_path):
    arquivo = tmp_path / "invalido.txt"
    arquivo.write_text(
        "#####\n"
        "#SXG#\n"
        "#####\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        ler_mapa(str(arquivo))