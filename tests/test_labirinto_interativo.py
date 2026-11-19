# [IA] Claude – testes do gerador do HTML interativo (só IO/formatação; usa um mapa fictício).
import json

import pytest

from src.labirinto_interativo import execucao_ok, execucao_status, gerar_html, numerar_bonus, rotulo

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


GRADE_BONUS = ["#######",
               "#S+.+G#",
               "#..+..#",
               "#######"]


def _dados(html):
    return json.loads(html.split("const DADOS = ")[1].split(";\n")[0])


def test_bonus_numerados_em_ordem_de_leitura():
    # bônus em (1,2), (1,4), (2,3) -> números 0, 1, 2
    assert numerar_bonus(GRADE_BONUS) == {(1, 2): 0, (1, 4): 1, (2, 3): 2}
    estado = ((2, 3), frozenset(), frozenset({(2, 3), (1, 2)}))
    assert rotulo(estado, GRADE_BONUS) == "(2,3)|-|{0,2}"


def test_rotulo_no_html_usa_numero_do_bonus(tmp_path):
    caminho = [((1, 1), frozenset(), frozenset()),
               ((1, 2), frozenset(), frozenset({(1, 2)}))]
    mapas = {"fake": {"grade": GRADE_BONUS, "execucoes": {"X": execucao_ok(caminho, [0, -4])}}}
    dados = _dados(gerar_html(mapas, tmp_path / "lab.html").read_text(encoding="utf-8"))
    p = dados["mapas"]["fake"]["execucoes"]["X"]["passos"][1]
    assert p["bonus"] == [0]
    assert p["rotulo"] == "(1,2)|-|{0}"


def test_bonus_em_casa_que_nao_e_bonus(tmp_path):
    caminho = [((1, 1), frozenset(), frozenset({(1, 1)}))]
    mapas = {"fake": {"grade": GRADE_BONUS, "execucoes": {"X": execucao_ok(caminho)}}}
    with pytest.raises(ValueError):
        gerar_html(mapas, tmp_path / "lab.html")


def test_armadilhas_entram_com_rotulo(tmp_path):
    armadilhas = [((2, 1), frozenset("a"), frozenset())]
    mapas = {"fake": {"grade": GRADE_BONUS, "execucoes": {"X": execucao_status("sem_solucao")},
                      "armadilhas": armadilhas}}
    dados = _dados(gerar_html(mapas, tmp_path / "lab.html").read_text(encoding="utf-8"))
    assert [a["rotulo"] for a in dados["mapas"]["fake"]["armadilhas"]] == ["(2,1)|a|{}"]
