import logging
from fastapi import HTTPException
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrai o texto de um arquivo PDF utilizando PyPDF2.
    Itera sobre cada página do PDF e concatena o texto extraído.
    """
    try:
        pdf_reader = PdfReader(pdf_file.file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.info("Texto extraído do PDF com sucesso.")
        return text
    except Exception as e:
        logger.error("Erro ao ler PDF: %s", str(e))
        raise HTTPException(status_code=400, detail="Erro ao ler o arquivo PDF: " + str(e))
