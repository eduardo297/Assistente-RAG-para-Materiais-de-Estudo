def extrair_texto_txt(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        texto = arquivo.read()

    informacoes = []

    # considera paragrafos separados por duas quebras de linha
    paragrafos = texto.split("\n\n")

    for i, paragrafo in enumerate(paragrafos):
        paragrafo = paragrafo.strip()

        if not paragrafo:
            continue

        informacoes.append({
            "texto": paragrafo,
            "metadados": {
                "fonte": caminho,
                "pagina": 1,  # Arquivos de texto não possuem informações de página, então definimos como 1
                "paragrafo": i + 1
            }
        })

    return informacoes