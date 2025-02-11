import os
from fastapi import FastAPI, HTTPException, Form
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

def gerar_resumo(acordao: str) -> str:
    """
    Gera o resumo de um acórdão utilizando a LLM.
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
    return executar_prompt(prompt)

@app.post("/comparar_acordaos")
def comparar_acordaos(acordao_1: str = Form(...), acordao_2: str = Form(...)):
    """
    Recebe dois acórdãos via formulário, gera os resumos de cada um e realiza a análise comparativa.
    """
    # Gera os resumos para cada acórdão
    resumo_1 = gerar_resumo(acordao_1)
    resumo_2 = gerar_resumo(acordao_2)
    
    # Cria o prompt para comparação
    prompt_comparativo = f"""
    Você é um assistente jurídico especializado em análise comparativa de acórdãos.
    
    **Acórdão 1 (Resumo):** 
    {resumo_1}

    **Acórdão 2 (Resumo):** 
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
    
    analise = executar_prompt(prompt_comparativo)
    
    return {"analise_comparativa": analise, "mensagem": "Comparação concluída com sucesso!"}
