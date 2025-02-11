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
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            stream=False,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na LLM: {str(e)}")


@app.post("/analisar_acordao_1")
def analisar_acordao_1(acordao: AcordaoInput):
    """
    Analisa e resume o primeiro acórdão utilizando a LLM.
    """
    prompt = f"""
    Você é um assistente jurídico especializado em análise de acórdãos.
    
    **Acórdão a ser analisado:**
    {acordao.texto}

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

    resumo = executar_prompt(prompt)

    # Salva o resumo em memória
    resumos_acordaos["acordao_1"] = resumo

    return {"resumo_acordao_1": resumo, "mensagem": "Primeiro acórdão processado. Envie o segundo acórdão."}


@app.post("/analisar_acordao_2")
def analisar_acordao_2(acordao: AcordaoInput):
    """
    Analisa e resume o segundo acórdão utilizando a LLM.
    """
    prompt = f"""
    Você é um assistente jurídico especializado em análise de acórdãos.
    
    **Acórdão a ser analisado:**
    {acordao.texto}

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

    resumo = executar_prompt(prompt)

    # Salva o resumo em memória
    resumos_acordaos["acordao_2"] = resumo

    return {"resumo_acordao_2": resumo, "mensagem": "Segundo acórdão processado. Agora você pode comparar os acórdãos."}


@app.post("/comparar_acordaos")
def comparar_acordaos():
    """
    Compara os dois acórdãos armazenados e identifica divergências utilizando a LLM.
    """
    # Recupera os resumos armazenados
    resumo_1 = resumos_acordaos.get("acordao_1", "")
    resumo_2 = resumos_acordaos.get("acordao_2", "")

    if not resumo_1 or not resumo_2:
        raise HTTPException(status_code=400, detail="Os resumos dos dois acórdãos ainda não foram gerados.")

    prompt = f"""
    Você é um assistente jurídico especializado em análise comparativa de acórdãos.
    
    **Acórdão 1:** 
    {resumo_1}

    **Acórdão 2:** 
    {resumo_2}

    **Tarefa:** 
    1. Compare os fatos e alegações apresentados em ambos os acórdãos.
    2. Analise as normas jurídicas utilizadas e destaque diferenças na fundamentação legal.
    3. Identifique se houve divergência na interpretação da lei federal entre os dois tribunais.
    4. Gere uma tabela comparativa com os principais pontos.

    **Formato da resposta:** 
    - Comparação dos Fatos:
    - Comparação das Alegações:
    - Diferenças na Fundamentação Jurídica:
    - Divergência na Decisão Final:
    - **Tabela Comparativa:**
    """

    analise = executar_prompt(prompt)

    return {"analise_comparativa": analise, "mensagem": "Comparação concluída com sucesso!"}
