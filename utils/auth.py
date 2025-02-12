import os
import logging
from fastapi import HTTPException, Header

logger = logging.getLogger(__name__)

def get_api_key(x_api_key: str = Header(...)):

    """
    Valida a API key presente no header 'x-api-key'.
    Compara o valor recebido com o esperado (definido no .env ou padrão).
    
    Args:
        x_api_key (str): Chave de API fornecida no header 'x-api-key'

    Returns:
        str: A chave de API validada

    Raises:
        HTTPException: Se a chave de API for inválida, levanta uma exceção 401

    Example:
        get_api_key("minha-chave-secreta")
        'minha-chave-secreta'

    Notes:
        - A chave esperada é definida pela variável de ambiente 'API_KEY'
        - Se 'API_KEY' não estiver definida, usa-se o valor padrão 'minha-chave-padrao'
        - Tentativas de acesso com chave inválida são registradas no log como warning
    """

    API_KEY_EXPECTED = os.getenv("API_KEY", "minha-chave-padrao")
    if x_api_key != API_KEY_EXPECTED:
        logger.warning("Tentativa de acesso com chave de API inválida: %s", x_api_key)
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    return x_api_key
