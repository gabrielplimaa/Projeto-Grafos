def ler_mapa(caminho):
    linhas = []
    with open (caminho, "r", encoding="utf-8") as file:
        for linha in file:
            if linha.startswith(";"):
                continue
            linhas.append(linha.rstrip("\r\n"))

    if (len(linhas) == 0):
        print("Erro: Mapa vazio")
        return
    
    qtd = len(linhas[0])

    for linha in linhas:
        if len(linha) != qtd:
            print("Erro: Mapa não retangular")
            return

    qtd_inicio = 0
    qtd_saida = 0

    for linha in linhas:
        qtd_inicio += linha.count("S")
        qtd_saida += linha.count("G")

    if qtd_inicio != 1:
        print("Erro: O mapa deve ter exatamente 1 início S")
        return

    if qtd_saida == 0:
        print("Erro: O mapa deve ter pelo menos uma saída G")
        return

    simbolos_permitidos = ["#", ".", "S", "G" ,",", "~", "a", "b", "c", "d", "A", "B", "C", "D", ">", "<", "^", "v", "+", "*"]
    for linha in linhas:
        for char in linha:
            if char not in simbolos_permitidos:
                print("Há algum caractere não permitido no mapa")
                return

    return linhas