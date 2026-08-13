import docx_loader
import pdf_loader
import pptx_loader
import txt_loader

loaders = {
        ".pdf": pdf_loader.extrair_texto_pdf,
        ".docx": docx_loader.extrair_texto_docx,
        ".pptx": pptx_loader.extrair_texto_pptx,
        ".txt": txt_loader.extrair_texto_txt,
    }

def retornar_loader_por_extensao(extensao: str):
    """Retorna a função de loader apropriada com base na extensão do arquivo."""
    return loaders.get(extensao.lower())