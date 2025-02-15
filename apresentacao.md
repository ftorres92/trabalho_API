
---

## 1. Visão Geral do Projeto

**Objetivos Principais:**

- **Resumo de Acórdãos:**  
  A API gera um resumo estruturado a partir do texto completo de um acórdão, contendo os fatos relevantes, as principais alegações, as normas jurídicas aplicadas e a decisão final.

- **Comparação de Acórdãos:**  
  Utilizando os resumos gerados (seja via entrada de texto ou extraídos de PDFs), a API realiza uma análise comparativa que destaca semelhanças e diferenças – desde os fatos e alegações até a fundamentação jurídica e a decisão final.

**Tecnologias e Práticas Utilizadas:**

- **FastAPI:** Para construir uma API de alta performance.
- **Groq (LLM):** Para processar prompts e gerar os resumos e comparações.
- **pypdf:** Para extrair texto de arquivos PDF.
- **dotenv:** Para o gerenciamento seguro de variáveis de ambiente.
- **Logging:** Para registro detalhado de operações e erros.
- **Autenticação via API Key:** Protege os endpoints, permitindo apenas acessos autorizados.
- **Versionamento:** Endpoints organizados sob o prefixo `/v1`, facilitando futuras atualizações sem quebrar a compatibilidade.

---

## 2. Estrutura do Projeto

Organizamos o código de forma modular para garantir clareza, manutenção e escalabilidade. A estrutura do projeto é a seguinte:

```
project/
├── main.py              # Arquivo principal que inicializa a aplicação
├── routers/
│   └── v1.py            # Endpoints da versão 1 da API
├── utils/
│   ├── auth.py          # Função de validação da API key
│   ├── llm.py           # Funções para interação com a LLM (Groq)
│   └── pdf_utils.py     # Função para extração de texto de PDFs
├── .env                 # Arquivo de variáveis de ambiente (não versionado)
├── .env.sample          # Exemplo das variáveis necessárias
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação e orientações de execução
```

Essa organização permite separar as responsabilidades:
- **main.py:** Cria a aplicação FastAPI, configura o logging e inclui os endpoints versionados.
- **routers/v1.py:** Contém todos os endpoints agrupados sob o prefixo `/v1` (versão 1 da API).
- **utils/auth.py:** Implementa a autenticação, validando a API key enviada via header.
- **utils/llm.py:** Responsável pela comunicação com a LLM (Groq), com funções para enviar prompts e gerar resumos.
- **utils/pdf_utils.py:** Contém a função para extrair o texto de arquivos PDF, permitindo o processamento de acórdãos em formato PDF.

---

## 3. Explicação Detalhada dos Componentes

### main.py

- **Carregamento das Variáveis de Ambiente:**  
  Usamos `load_dotenv()` para ler as variáveis definidas no arquivo `.env`. Isso garante que informações sensíveis, como chaves de API, não estejam hardcoded no código.

- **Configuração do Logging:**  
  Configuramos o logging com:
  ```python
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  ```
  Isso permite que todas as operações importantes e erros sejam registrados.

- **Inicialização da Aplicação:**  
  Criamos a aplicação FastAPI com metadados (título, versão, descrição e contato) e incluímos o router versionado:
  ```python
  app = FastAPI(
      title="API de Análise Comparativa de Acórdãos",
      version="1.0",
      description="Serviços de IA para resumo e comparação de acórdãos (texto e PDF), com o objetivo de auxiliar na elaboração de Recurso Especial",
      contact={"name": "Fernando Torres, Fernando Lobo, Marcio Ferreira", "url": "http://github.com/ftorres92/"}
  )
  app.include_router(v1.router)
  ```

### utils/auth.py

- **Função get_api_key:**  
  Essa função valida o header `x-api-key` comparando-o com o valor esperado (definido no `.env` ou um valor padrão). Se a chave não corresponder, ela registra um warning e lança uma `HTTPException` com status 401:
  ```python
  if x_api_key != API_KEY_EXPECTED:
      logger.warning("Tentativa de acesso com chave de API inválida: %s", x_api_key)
      raise HTTPException(status_code=401, detail="Chave de API inválida")
  ```
  Essa validação é utilizada em todos os endpoints críticos por meio da dependência `Depends(get_api_key)`.

### utils/llm.py

- **Configuração do Serviço LLM (Groq):**  
  Carregamos a chave da API Groq e definimos o modelo a ser utilizado:
  ```python
  GROQ_API_KEY = os.getenv("GROQ_API_KEY")
  MODEL_NAME = "llama3-70b-8192"
  ```
  Se a chave não estiver definida, o código interrompe a execução com uma mensagem detalhada.

- **Função executar_prompt:**  
  Essa função envia um prompt para a LLM e retorna a resposta. Em caso de erro, registra o erro e lança uma `HTTPException` com status 500:
  ```python
  try:
      response = client.chat.completions.create( ... )
      logger.info("Prompt executado com sucesso.")
      return response.choices[0].message.content
  except Exception as e:
      logger.error("Erro na LLM: %s", str(e))
      raise HTTPException(status_code=500, detail=f"Erro na LLM: {str(e)}")
  ```

- **Função gerar_resumo:**  
  Recebe o texto de um acórdão, monta um prompt detalhado para resumir o documento e utiliza `executar_prompt` para obter o resumo. O prompt contém instruções específicas sobre o formato da resposta, salvando-a em um dicionário:
  ```python
  prompt = f"""
  Você é um assistente jurídico especializado em análise de acórdãos.
  
  **Acórdão a ser analisado:**
  {acordao}
  
  **Tarefa:** 
  1. Resuma os fatos relevantes...
  """
  logger.info("Gerando resumo do acórdão...")
  return executar_prompt(prompt)
  ```

### utils/pdf_utils.py

- **Função extract_text_from_pdf:**  
  Essa função utiliza a biblioteca `pypdf` para ler o arquivo PDF e extrair o texto de cada página. Se ocorrer algum erro durante a extração, ela registra o erro e lança uma `HTTPException` com status 400:
  ```python
  try:
      reader = PdfReader(pdf_file.file)
      for page in reader.pages:
          ...
      logger.info("Texto extraído do PDF com sucesso.")
      return text
  except Exception as e:
      logger.error("Erro ao ler PDF: %s", str(e))
      raise HTTPException(status_code=400, detail="Erro ao ler o arquivo PDF: " + str(e))
  ```

### routers/v1.py

Este módulo contém os endpoints agrupados sob o prefixo `/v1`, organizando duas abordagens:

#### Versão TEXTO (Endpoint Único)
- **Endpoint `/comparar_acordaos_text`:**  
  Recebe dois acórdãos via formulário, garantindo que os dados sejam do tipo string (utilizando `Form`).  
  Realiza validações (por exemplo, pode ser implementada a verificação para rejeitar entradas que contenham apenas números).  
  Gera resumos para cada acórdão usando a função `gerar_resumo` e monta um prompt para comparação:
  ```python
  def comparar_acordaos_text(acordao_1: str = Form(...), acordao_2: str = Form(...)):
      logger.info("Iniciando comparação de acórdãos (versão TEXTO).")
      resumo_1 = gerar_resumo(acordao_1)
      resumo_2 = gerar_resumo(acordao_2)
      ...
      logger.info("Comparação (TEXTO) concluída com sucesso.")
      return {"analise_comparativa": analise, ...}
  ```

#### Versão PDF (Sequência de Endpoints)
- **Endpoint `/analisar_acordao_pdf_1`:**  
  Recebe o primeiro arquivo PDF (usando `UploadFile = File(...)`), extrai o texto e gera um resumo, armazenando-o em memória.
- **Endpoint `/analisar_acordao_pdf_2`:**  
  Processa o segundo PDF da mesma forma e armazena o resumo.
- **Endpoint `/comparar_acordaos_pdf`:**  
  Recupera os resumos armazenados e monta um prompt comparativo para a análise final. Verifica se ambos os resumos foram gerados e, caso contrário, lança uma `HTTPException`:
  ```python
  if not resumo_1 or not resumo_2:
      logger.error("Resumos incompletos: primeiro ou segundo acórdão não processado.")
      raise HTTPException(status_code=400, detail="Os resumos de ambos os acórdãos não foram gerados...")
  ```

Todos esses endpoints incluem a dependência `Depends(get_api_key)` para garantir que somente requisições autenticadas (via header `x-api-key`) sejam processadas.

---

## 4. Diferenciais Técnicos

- **Validação de Dados:** Com uso de `Form` e `UploadFile`, além de validações customizadas.
- **Tratamento de Erros:** Através de `HTTPException` com mensagens e códigos apropriados.
- **Logs:** Registros detalhados que possibilitam monitoramento e resolução de problemas.
- **Segurança:** Implementação robusta de autenticação via API key.
- **Versionamento:** Organização dos endpoints sob `/v1`, permitindo evoluções sem quebrar a compatibilidade.

### Validação de Dados
- **Uso de `Form` e `UploadFile`:**  
  Nos endpoints de texto e PDF (em `routers/v1.py`), usamos:
  ```python
  acordao_1: str = Form(...), acordao: UploadFile = File(...)
  ```
  Isso força a entrada de dados no formato correto.

### Tratamento de Erros
- **HTTPException em Diversos Pontos:**  
  - **Autenticação:**  
    Em `utils/auth.py`, se a API key for inválida:
    ```python
    raise HTTPException(status_code=401, detail="Chave de API inválida")
    ```
  - **Erro na LLM:**  
    Em `utils/llm.py`, se ocorrer algum erro na comunicação com a LLM:
    ```python
    raise HTTPException(status_code=500, detail=f"Erro na LLM: {str(e)}")
    ```
  - **Erro na Extração de PDF:**  
    Em `utils/pdf_utils.py`:
    ```python
    raise HTTPException(status_code=400, detail="Erro ao ler o arquivo PDF: " + str(e))
    ```
  - **Verificação de Resumos Inexistentes:**  
    No endpoint `/comparar_acordaos_pdf` (em `routers/v1.py`), se um dos resumos não estiver disponível:
    ```python
    raise HTTPException(status_code=400, detail="Os resumos de ambos os acórdãos não foram gerados...")
    ```

### Logs
- **Configuração Global:**  
  Em `main.py`, definimos:
  ```python
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  ```
- **Logs de INFO e ERROR:**  
  - Em `utils/llm.py`:  
    ```python
    logger.info("Prompt executado com sucesso.")
    logger.error("Erro na LLM: %s", str(e))
    ```
  - Em `utils/pdf_utils.py`:  
    ```python
    logger.info("Texto extraído do PDF com sucesso.")
    logger.error("Erro ao ler PDF: %s", str(e))
    ```
  - Nos endpoints em `routers/v1.py`:  
    São registrados logs como:
    ```python
    logger.info("Iniciando comparação de acórdãos (versão TEXTO).")
    logger.info("Comparação (TEXTO) concluída com sucesso.")
    ```
  Esses logs permitem monitorar o fluxo da aplicação e identificar problemas rapidamente.

### Segurança
- **Autenticação via API Key:**  
  Implementada em `utils/auth.py` e aplicada em todos os endpoints através de `Depends(get_api_key)`. Isso garante que somente clientes com a chave correta acessem os serviços.

### Versionamento
- **Endpoints Versionados:**  
  Todos os endpoints estão agrupados sob o prefixo `/v1` (definido em `routers/v1.py`), permitindo a criação de futuras versões sem afetar a compatibilidade com clientes existentes.
- **Estrutura Modular:**  
  A divisão em pastas (`routers`, `utils`) facilita a evolução do projeto, permitindo adição de novas funcionalidades ou versões de forma organizada.

---




