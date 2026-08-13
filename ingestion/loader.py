from ingestion import docx_loader
from ingestion import pdf_loader
from ingestion import pptx_loader
from ingestion import txt_loader

loaders = {
        ".pdf": pdf_loader.extrair_texto_pdf,
        ".docx": docx_loader.extrair_texto_docx,
        ".pptx": pptx_loader.extrair_texto_pptx,
        ".txt": txt_loader.extrair_texto_txt,
    }

def retornar_loader_por_extensao(extensao: str):
    """Retorna a função de loader apropriada com base na extensão do arquivo."""
    return loaders.get(extensao.lower())