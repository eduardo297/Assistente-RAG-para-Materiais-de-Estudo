import os

from dotenv import load_dotenv
from google import genai
import time
from google.genai import errors as genai_errors

load_dotenv()


def criar_cliente_gemini():
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
as informações presentes no contexto abaixo
e mostre a fonte da informação.

Se a resposta não estiver no contexto,
diga claramente que não encontrou essa
informação nos materiais.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
"""



def gerar_resposta(cliente, pergunta: str, trechos: list[str], max_tentativas: int = 5) -> str:
    """Gera a resposta via Gemini, com retry em caso de sobrecarga do servidor (503)."""

   
    prompt = montar_prompt(
            pergunta,
            trechos
        )
    for tentativa in range(1, max_tentativas + 1):
        try:
            resposta = cliente.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            return resposta.text

        except genai_errors.ServerError as erro:
            if tentativa == max_tentativas:
                raise

            espera = 2 ** tentativa  # 2s, 4s, 8s, 16s, 32s
            print(
                f"  -> Gemini sobrecarregado (tentativa {tentativa}/{max_tentativas}), "
                f"aguardando {espera}s..."
            )
            time.sleep(espera)


