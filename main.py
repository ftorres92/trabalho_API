import os
import logging
from fastapi import FastAPI, APIRouter, HTTPException, Form, UploadFile, File, Depends, Header
from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Carrega variáveis do .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia o FastAPI com título e versão
app = FastAPI(
    title="API de Análise Comparativa de Acórdãos",
    version="1.0",
    description="Serviços de IA para resumo e comparação de acórdãos (texto e PDF)"
)

# Criação do router com prefixo /v1 (versionamento)
router = APIRouter(prefix="/v1")

# Configuração da API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama3-70b-8192"  # Modelo da Groq que será utilizado

if not GROQ_API_KEY:
    raise ValueError("A variável de ambiente GROQ_API_KEY não está definida!")

client = Groq(api_key=GROQ_API_KEY)

# Dependência de segurança: validação da API key (passada no header x-api-key)
def get_api_key(x_api_key: str = Header(...)):
    API_KEY_EXPECTED = os.getenv("API_KEY", "minha-chave-padrao")
    if x_api_key != API_KEY_EXPECTED:
        logger.warning("Tentativa de acesso com chave de API inválida: %s", x_api_key)
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    return x_api_key

def executar_prompt(prompt: str) -> str:
    """
    Envia um prompt para a LLM via Groq e retorna a resposta gerada.
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
    logger.info("Gerando resumo do acórdão...")
    return executar_prompt(prompt)

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """
    Extrai o texto de um arquivo PDF utilizando o PyPDF2.
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

# -------------------------
# Versão com entrada em TEXTO
# -------------------------
@router.post("/comparar_acordaos_text", dependencies=[Depends(get_api_key)])
def comparar_acordaos_text(acordao_1: str = Form(...), acordao_2: str = Form(...)):
    """
    Recebe dois acórdãos via formulário (em formato de texto), gera os resumos e realiza a análise comparativa.
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

# -------------------------
# Versão com upload de ARQUIVOS PDF
# -------------------------
# Dicionário para armazenar os resumos dos acórdãos processados via PDF.
resumos_acordaos = {}

@router.post("/analisar_acordao_pdf_1", dependencies=[Depends(get_api_key)])
def analisar_acordao_pdf_1(acordao: UploadFile = File(...)):
    """
    Recebe o primeiro arquivo PDF, extrai o texto, gera o resumo e o armazena.
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
    Recebe o segundo arquivo PDF, extrai o texto, gera o resumo e o armazena.
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
    Realiza a comparação dos resumos gerados a partir dos PDFs enviados previamente.
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

# Inclui o router versionado na aplicação
app.include_router(router)
