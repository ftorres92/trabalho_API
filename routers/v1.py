import logging
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from utils.auth import get_api_key
from utils.llm import gerar_resumo, executar_prompt
from utils.pdf_utils import extract_text_from_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1")

# Dicionário para armazenar os resumos dos acórdãos enviados via PDF.
resumos_acordaos = {}

@router.post("/comparar_acordaos_text", dependencies=[Depends(get_api_key)])
def comparar_acordaos_text(acordao_1: str = Form(...), acordao_2: str = Form(...)):
    """
    Endpoint para comparar dois acórdãos enviados como texto.
    - Gera um resumo para cada acórdão utilizando a LLM.
    - Monta um prompt para comparar os resumos e retorna a análise comparativa.
    """
    logger.info("Iniciando comparação de acórdãos (versão TEXTO).")
    resumo_1 = gerar_resumo(acordao_1)
    resumo_2 = gerar_resumo(acordao_2)
    
    prompt_comparativo = f"""
Você é um assistente jurídico especializado em análise comparativa de acórdãos.

**Acórdão 1 (Resumo):** 
{resumo_1}

**Acórdão 2 (Resumo):** 
{resumo_2}

**Tarefa:** 
1. Compare os fatos e as alegações apresentados em ambos os acórdãos.
2. Analise as normas jurídicas utilizadas e destaque diferenças na fundamentação legal.
3. Identifique se houve divergência na interpretação da lei federal entre os dois tribunais.
4. Gere uma tabela comparativa com os principais pontos.

**Formato da resposta:** 
- Comparação dos Fatos:
- Comparação das Alegações:
- Diferenças na Fundamentação Jurídica:
- Divergência na Decisão Final:
- Tabela Comparativa:
"""
    analise = executar_prompt(prompt_comparativo)
    logger.info("Comparação (TEXTO) concluída com sucesso.")
    return {"analise_comparativa": analise, "mensagem": "Comparação concluída com sucesso (versão TEXTO)!"}

@router.post("/analisar_acordao_pdf_1", dependencies=[Depends(get_api_key)])
def analisar_acordao_pdf_1(acordao: UploadFile = File(...)):
    """
    Endpoint para processar o primeiro acórdão enviado em formato PDF.
    - Extrai o texto do PDF.
    - Gera o resumo do acórdão.
    - Armazena o resumo para posterior comparação.
    """
    logger.info("Processando primeiro acórdão (PDF).")
    texto = extract_text_from_pdf(acordao)
    resumo = gerar_resumo(texto)
    resumos_acordaos["acordao_1"] = resumo
    logger.info("Primeiro acórdão (PDF) processado com sucesso.")
    return {"resumo_acordao_1": resumo, "mensagem": "Primeiro acórdão processado com sucesso (PDF)."}

@router.post("/analisar_acordao_pdf_2", dependencies=[Depends(get_api_key)])
def analisar_acordao_pdf_2(acordao: UploadFile = File(...)):
    """
    Endpoint para processar o segundo acórdão enviado em formato PDF.
    - Extrai o texto do PDF.
    - Gera o resumo do acórdão.
    - Armazena o resumo para posterior comparação.
    """
    logger.info("Processando segundo acórdão (PDF).")
    texto = extract_text_from_pdf(acordao)
    resumo = gerar_resumo(texto)
    resumos_acordaos["acordao_2"] = resumo
    logger.info("Segundo acórdão (PDF) processado com sucesso.")
    return {"resumo_acordao_2": resumo, "mensagem": "Segundo acórdão processado com sucesso (PDF)."}

@router.post("/comparar_acordaos_pdf", dependencies=[Depends(get_api_key)])
def comparar_acordaos_pdf():
    """
    Endpoint para comparar os acórdãos processados via PDF.
    - Recupera os resumos gerados previamente.
    - Monta um prompt comparativo e retorna a análise realizada pela LLM.
    """
    logger.info("Iniciando comparação de acórdãos (versão PDF).")
    resumo_1 = resumos_acordaos.get("acordao_1")
    resumo_2 = resumos_acordaos.get("acordao_2")
    
    if not resumo_1 or not resumo_2:
        logger.error("Resumos incompletos: primeiro ou segundo acórdão não processado.")
        raise HTTPException(
            status_code=400,
            detail="Os resumos de ambos os acórdãos não foram gerados. Por favor, processe ambos antes de comparar."
        )
    
    prompt_comparativo = f"""
Você é um assistente jurídico especializado em análise comparativa de acórdãos.

**Acórdão 1 (Resumo):** 
{resumo_1}

**Acórdão 2 (Resumo):** 
{resumo_2}

**Tarefa:** 
1. Compare os fatos e as alegações apresentados em ambos os acórdãos.
2. Analise as normas jurídicas utilizadas e destaque diferenças na fundamentação legal.
3. Identifique se houve divergência na interpretação da lei federal entre os dois tribunais.
4. Gere uma tabela comparativa com os principais pontos.

**Formato da resposta:** 
- Comparação dos Fatos:
- Comparação das Alegações:
- Diferenças na Fundamentação Jurídica:
- Divergência na Decisão Final:
- Tabela Comparativa:
"""
    analise = executar_prompt(prompt_comparativo)
    logger.info("Comparação (PDF) concluída com sucesso.")
    return {"analise_comparativa": analise, "mensagem": "Comparação concluída com sucesso (versão PDF)!"}
