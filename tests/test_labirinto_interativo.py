# [IA] Claude – testes do gerador do HTML interativo (só IO/formatação; usa um mapa fictício).
import json

import pytest

from src.labirinto_interativo import execucao_ok, execucao_status, gerar_html, rotulo

GRADE = ["#####",
         "#S.G#",
         "#####"]
CAMINHO = [((1, 1), frozenset()), ((1, 2), frozenset()), ((1, 3), frozenset())]


def test_rotulo_no_formato_do_enunciado():
    assert rotulo(((1, 1), frozenset())) == "(1,1)|-|{}"
    assert rotulo(((3, 5), frozenset("ba"), frozenset({2, 0}))) == "(3,5)|ab|{0,2}"


def test_gera_html_com_dados_embutidos(tmp_path):
    mapas = {"fake": {"grade": GRADE, "execucoes": {"X": execucao_ok(CAMINHO, [0, 1, 2])}}}
    saida = gerar_html(mapas, tmp_path / "lab.html")
    html = saida.read_text(encoding="utf-8")
    assert "/*__DADOS__*/null" not in html
    dados = json.loads(html.split("const DADOS = ")[1].split(";\n")[0])
    assert [p["pos"] for p in dados["mapas"]["fake"]["execucoes"]["X"]["passos"]] == [[1, 1], [1, 2], [1, 3]]


def test_infinito_vira_null():
    execucao = execucao_ok(CAMINHO, [0, 1, float("inf")])
    assert execucao["passos"][2]["custo"] is None


def test_recusa_passo_em_parede(tmp_path):
    ruim = [((0, 0), frozenset())]
    mapas = {"fake": {"grade": GRADE, "execucoes": {"X": execucao_ok(ruim)}}}
    with pytest.raises(ValueError):
        gerar_html(mapas, tmp_path / "lab.html")


def test_status_invalido():
    with pytest.raises(ValueError):
        execucao_status("talvez")
