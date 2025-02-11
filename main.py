import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from groq import Groq
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

app = FastAPI()

# Configuração da API Groq
API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama3-70b-8192"  # Modelo da Groq que será utilizado

if not API_KEY:
    raise ValueError("A variável de ambiente GROQ_API_KEY não está definida!")

client = Groq(api_key=API_KEY)

# Armazena os resumos dos acórdãos temporariamente
resumos_acordaos = {}

# Modelos de entrada
class AcordaoInput(BaseModel):
    texto: str

# Função para executar prompts na LLM
def executar_prompt(prompt: str) -> str:
    """
    Envia um prompt para a Groq LLM e retorna a resposta gerada.
    """
    try:
        response = client.