import logging
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from utils.auth import get_api_key
from utils.llm import gerar_resumo, executar_prompt
from utils.pdf_utils import extract_text_from_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1")

# Dicionário para armazenar os resumos dos acórdãos enviados via PDF.
resumos_acordaos = {}

@router.post("/comparar_acordaos_text",tags=["primeira forma- endpoint único"], dependencies=[Depends(get_api_key)])

def comparar_acordaos_text(acordao_1: str = Form(...), acordao_2: str = Form(...)):
    """
    Endpoint para comparar dois acórdãos enviados como texto.
    - Gera um resumo para cada acórdão utilizando a LLM.
    - Monta um prompt para comparar os resumos e retorna a análise comparativa.
        ----------
        acordao_1 : str
            Texto completo do primeiro acórdão a ser comparado
        acordao_2 : str
            Texto completo do segundo acórdão a ser comparado
        Returns
        -------
        dict
            Dicionário contendo:
                - analise_comparativa: str
                    Análise detalhada comparando os dois acórdãos, incluindo:
                    * Comparação dos fatos
                    * Comparação das alegações
                    * Diferenças na fundamentação jurídica
                    * Divergência na decisão final
                    * Tabela comparativa
                - mensagem: str
                    Mensagem indicando o sucesso da operação
        Requires
        --------
        API Key válida através da dependência get_api_key
        Notes
        -----
        A comparação é feita em várias etapas:
        1. Geração de resumos para cada acórdão
        2. Criação de um prompt especializado para análise comparativa
        3. Processamento através de LLM para gerar a análise final
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


"""
-----------------------
SEGUNDA FORMA- ENDPOINT QUE RESUME OS ACÓRDÃOS E OUTRO QUE REALIZA A COMPARAÇÃO ENTRE ELES
-----------------------
"""


@router.post("/analisar_acordao_pdf_1", tags=["segunda forma- três endpoints"], dependencies=[Depends(get_api_key)])

def analisar_acordao_pdf_1(acordao: UploadFile = File(...)):
    """
    Endpoint para processar o primeiro acórdão enviado em formato PDF.
    - Extrai o texto do PDF.
    - Gera o resumo do acórdão.
    - Armazena o resumo para posterior comparação.

    Parâmetros:
    acordao (UploadFile): Arquivo PDF contendo o acórdão a ser analisado

    Retorna:
        dict: Dicionário contendo:
            - resumo_acordao_1: Texto do resumo gerado para o acórdão
            - mensagem: Mensagem de confirmação do processamento

    Fluxo:
        1. Extrai o texto do arquivo PDF
        2. Gera um resumo do texto extraído
        3. Armazena o resumo em memória para posterior comparação

    Dependências:
        - Requer autenticação via API key (get_api_key)

    Raises:
        HTTPException: Se houver erro no processamento do arquivo ou geração do resumo
    """
    logger.info("Processando primeiro acórdão (PDF).")
    texto = extract_text_from_pdf(acordao)
    resumo = gerar_resumo(texto)
    resumos_acordaos["acordao_1"] = resumo
    logger.info("Primeiro acórdão (PDF) processado com sucesso.")
    return {"resumo_acordao_1": resumo, "mensagem": "Primeiro acórdão processado com sucesso (PDF)."}


@router.post("/analisar_acordao_pdf_2", tags=["segunda forma- três endpoints"], dependencies=[Depends(get_api_key)])
def analisar_acordao_pdf_2(acordao: UploadFile = File(...)):
    """
    Endpoint para processar o segundo acórdão enviado em formato PDF.(....)
    """
    logger.info("Processando segundo acórdão (PDF).")
    texto = extract_text_from_pdf(acordao)
    resumo = gerar_resumo(texto)
    resumos_acordaos["acordao_2"] = resumo
    logger.info("Segundo acórdão (PDF) processado com sucesso.")
    return {"resumo_acordao_2": resumo, "mensagem": "Segundo acórdão processado com sucesso (PDF)."}

@router.post("/comparar_acordaos_pdf", tags=["segunda forma- três endpoints"], dependencies=[Depends(get_api_key)])

def comparar_acordaos_pdf():
    """
    Endpoint para comparar dois acórdãos processados via PDF.
    Este endpoint realiza uma análise comparativa entre dois acórdãos previamente 
    processados e armazenados em memória. A comparação é feita através de um modelo
    de linguagem que analisa os resumos gerados anteriormente.
    Returns:
        dict: Um dicionário contendo:
            - analise_comparativa (str): Análise detalhada comparando os dois acórdãos
            - mensagem (str): Mensagem indicando o sucesso da operação
    Raises:
        HTTPException: 
            - status_code=400: Se um ou ambos os resumos dos acórdãos não foram 
            previamente processados e armazenados.
    Dependências:
        - Requer autenticação via API key (dependency: get_api_key)
        - Requer que os resumos dos acórdãos tenham sido previamente gerados e 
        armazenados em 'resumos_acordaos'
    Notas:
        A análise comparativa inclui:
        - Comparação dos fatos apresentados
        - Comparação das alegações
        - Análise das diferenças na fundamentação jurídica
        - Identificação de divergências na interpretação da lei federal
        - Tabela comparativa com os principais pontos
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
