import os
import logging
from fastapi import HTTPException, Header

logger = logging.getLogger(__name__)

def get_api_key(x_api_key: str = Header(...)):
    """
    Valida a API key presente no header 'x-api-key'.
    Compara o valor recebido com o esperado (definido no .env ou padrão).
    """
    API_KEY_EXPECTED = os.getenv("API_KEY", "minha-chave-padrao")
    if x_api_key != API_KEY_EXPECTED:
        logger.warning("Tentativa de acesso com chave de API inválida: %s", x_api_key)
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    return x_api_key
