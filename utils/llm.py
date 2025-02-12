import os
import logging
from fastapi import HTTPException
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configuração da API Groq e definição do modelo
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama3-70b-8192"  # Modelo da Groq que será utilizado

if not GROQ_API_KEY:
    raise ValueError("A variável de ambiente GROQ_API_KEY não está definida!")

# Criação do cliente Groq para interagir com a LLM
client = Groq(api_key=GROQ_API_KEY)

def executar_prompt(prompt: str) -> str:
    """
    Envia um prompt para a LLM via Groq e retorna a resposta gerada.
    Em caso de erro, lança uma exceção HTTP.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            stream=False,
        )
        logger.info("Prompt executado com sucesso.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error("Erro na LLM: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erro na LLM: {str(e)}")

def gerar_resumo(acordao: str) -> str:
    """
    Gera um resumo para o acórdão fornecido.
    Prepara um prompt detalhado para instruir a LLM a resumir o texto e retorna o resultado.
    """
    prompt = f"""
Você é um assistente jurídico especializado em análise de acórdãos.

**Acórdão a ser analisado:**
{acordao}

**Tarefa:** 
1. Resuma os fatos relevantes do acórdão.
2. Identifique as principais alegações das partes.
3. Explique quais normas jurídicas foram aplicadas.
4. Apresente a decisão final do tribunal.

**Formato da resposta:** 
- Fatos Relevantes:
- Alegações Principais:
- Normas Aplicadas:
- Decisão Final:
"""
    logger.info("Gerando resumo do acórdão...")
    return executar_prompt(prompt)
