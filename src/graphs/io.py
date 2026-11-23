def ler_mapa(caminho):
    linhas = []
    with open(caminho, "r", encoding="utf-8") as file:
        for linha in file:
            if linha.startswith(";"):
                continue
            linhas.append(linha.rstrip("\r\n"))

    while linhas and linhas[-1].strip() == "":
        linhas.pop()

    if len(linhas) == 0:
        raise ValueError("Mapa vazio")

    qtd = len(linhas[0])
    for linha in linhas:
        if len(linha) != qtd:
            raise ValueError("Mapa não retangular")

    qtd_inicio = 0
    qtd_saida = 0

    for linha in linhas:
        qtd_inicio += linha.count("S")
        qtd_saida += linha.count("G")

    if qtd_inicio != 1:
        raise ValueError("O mapa deve ter exatamente 1 início S")

    if qtd_saida == 0:
        raise ValueError("O mapa deve ter pelo menos uma saída G")

    simbolos_permitidos = ["#", ".", "S", "G" ,",", "~", "a", "b", "c", "d", "A", "B", "C", "D", ">", "<", "^", "v", "+", "*"]
    for linha in linhas:
        for char in linha:
            if char not in simbolos_permitidos:
                raise ValueError(f"Caractere não permitido no mapa: {char!r}")

    return linhas