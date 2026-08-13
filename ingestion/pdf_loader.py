from pypdf import PdfReader

def extrair_texto_pdf(caminho_pdf: str):
    """Extrai o texto de um PDF e separa em parágrafos."""

    leitor = PdfReader(caminho_pdf)
    informacoes = []

    numero_paragrafo = 1

    for pagina in leitor.pages:
        texto_pagina = pagina.extract_text() or ""

        if not texto_pagina.strip():
            continue

        paragrafos = texto_pagina.split("\n\n")

        for paragrafo in paragrafos:
            paragrafo = paragrafo.strip()

            if not paragrafo:
                continue

            informacoes.append({
                "texto": paragrafo,
                "metadados": {
                    "fonte": caminho_pdf,
                    "paragrafo": numero_paragrafo
                }
            })

            numero_paragrafo += 1

    return informacoes