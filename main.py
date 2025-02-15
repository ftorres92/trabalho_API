import os

import logging
from fastapi import FastAPI
from routers import v1  # importa o router da versão 1
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI com metadados
app = FastAPI(
    title="API de Análise Comparativa de Acórdãos",
    version="1.0",
    description="Serviços de IA para resumo e comparação de acórdãos (texto e PDF), com o objetivo de auxiliar na elaboração de Recurso Especial", 
    contact={
        "name": "Fernando Torres, Fernando Lobo, Marcio Ferreira",
        "url": "http://github.com/ftorres92/"},
)

# Inclui o router com prefixo /v1 na aplicação
app.include_router(v1.router)
