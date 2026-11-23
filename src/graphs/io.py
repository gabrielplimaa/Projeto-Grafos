SIMBOLOS_VALIDOS = set("#.SG,~abcdABCD><^v+*")


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