# API de Análise Comparativa de Acórdãos

Esta API permite comparar acórdãos jurídicos através de dois métodos de entrada:

- **Versão TEXTO:** Envio dos acórdãos como conteúdo textual via formulário.
- **Versão PDF:** Upload dos acórdãos em formato PDF, com extração do texto e geração dos resumos.

---

## Orientações para Executar a API

**Sugestão de versão do Python:** 3.10 ou superior

### 1. Criação e Ativação do Ambiente Virtual

Crie o ambiente virtual:
```bash
python -m venv venv
```

Ative o ambiente virtual:

- **No Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **No Linux/MacOS:**
  ```bash
  source venv/bin/activate
  ```

### 2. Instalação das Bibliotecas

Instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

Copie o arquivo `.env.sample` para `.env` e preencha as variáveis necessárias (por exemplo, a variável `GROQ_API_KEY`):

- **No Linux/MacOS:**
  ```bash
  cp .env.sample .env
  ```
- **No Windows:**
  ```bash
  copy .env.sample .env
  ```

### 4. Execução da API

Para executar a API em ambiente de desenvolvimento:
```bash
fastapi dev main.py
```

Para executar a API em ambiente de produção:
```bash
fastapi run main.py
```

## Endpoints Disponíveis

### Versão TEXTO

**POST /comparar_acordaos_text**  
Recebe dois acórdãos em formato de texto via formulário, gera os resumos e realiza a análise comparativa.

### Versão PDF

**POST /analisar_acordao_pdf_1**  
Recebe o primeiro arquivo PDF, extrai o texto, gera o resumo e o armazena.

**POST /analisar_acordao_pdf_2**  
Recebe o segundo arquivo PDF, extrai o texto, gera o resumo e o armazena.

**POST /comparar_acordaos_pdf**  
Utiliza os resumos gerados a partir dos PDFs para realizar a análise comparativa.

## Observações

**Armazenamento dos Resumos (Versão PDF):**  
Nesta implementação, os resumos dos acórdãos processados via PDF são armazenados em memória (variável global). Em ambientes com múltiplos usuários, recomenda-se utilizar uma estratégia de armazenamento mais robusta, como um banco de dados ou um mecanismo de sessão.

**Limitações de Tokens:**  
Certifique-se de que os textos enviados para a LLM não excedam os limites de tokens do modelo. Se necessário, adote técnicas de chunking para dividir textos muito longos.

Com estas instruções você estará pronto para executar a API e comparar acórdãos utilizando o método que melhor se adequar às suas necessidades.

