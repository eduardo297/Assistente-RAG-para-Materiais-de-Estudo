import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def criar_cliente():
    """Cria o cliente da API do Gemini."""

    return genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )


def montar_prompt(
    pergunta: str,
    trechos: list[str]
) -> str:
    """
    Monta o prompt que será enviado ao Gemini.
    """

    contexto = "\n\n---\n\n".join(trechos)

    return f"""
Você é um assistente de estudos.

Responda a pergunta do aluno usando APENAS
as informações presentes no contexto abaixo.

Se a resposta não estiver no contexto,
diga claramente que não encontrou essa
informação nos materiais.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
"""


def gerar_resposta(
    cliente,
    pergunta: str,
    trechos: list[str]
):
    """
    Gera uma resposta usando os trechos recuperados.
    """

    prompt = montar_prompt(
        pergunta,
        trechos
    )

    resposta = cliente.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return resposta.text