from docx import Document


def extrair_texto_docx(caminho):
    documento = Document(caminho)

    informacoes = []

    for i, paragrafo in enumerate(documento.paragraphs):
        texto = paragrafo.text.strip()

        if not texto:
            continue

        informacoes.append({
            "texto": texto,
            "metadados": {
                "fonte": caminho,
                "pagina": 1,  # O python-docx não fornece informações de página, então definimos como 1
                "paragrafo": i + 1
            }
        })

    return informacoes
