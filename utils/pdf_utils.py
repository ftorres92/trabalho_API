import logging
from fastapi import HTTPException
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> str:

    """
        Extrai o texto de um arquivo PDF.

    Args:
        pdf_file: Arquivo PDF enviado através de um FastAPI UploadFile.

    Returns:
        str: Texto extraído do PDF, com quebras de linha entre as páginas.

    Raises:
        HTTPException: Se houver erro na leitura do arquivo PDF, retorna erro 400
            com mensagem detalhada.

    Exemplos:
        pdf_file = UploadFile(...)
        text = extract_text_from_pdf(pdf_file)
        print(text)
        'Conteúdo da página 1\nConteúdo da página 2\n...'
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
