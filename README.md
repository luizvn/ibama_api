# API de Autos de Infração Ambiental - IBAMA

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-blue?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-blue?logo=sqlalchemy)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)

## Sobre o Projeto

A **API IBAMA** é uma solução de backend robusta e de alta performance, projetada para a ingestão, processamento e consulta de dados públicos sobre autos de infração ambiental emitidos pelo IBAMA. O principal desafio deste projeto é o processamento eficiente de arquivos CSV de múltiplos gigabytes, garantindo que os dados sejam validados, processados e armazenados de forma assíncrona, sem impactar a disponibilidade da API.

Este projeto foi construído utilizando as mais modernas ferramentas do ecossistema Python, com uma arquitetura **"Async-First"** e foco em boas práticas de desenvolvimento, escalabilidade e manutenibilidade.

---

## 🗃️ Fonte dos Dados

A API consome os dados públicos de autos de infração e sanções ambientais, que são abertamente disponibilizados pelo IBAMA através do Portal de Dados Abertos do Governo Federal.

Os conjuntos de dados originais, em formato CSV, que servem de insumo para a funcionalidade de ingestão desta API podem ser encontrados e baixados no seguinte link:

* **Link Oficial:** [**Fiscalização - Auto de Infração**](https://dados.gov.br/dados/conjuntos-dados/fiscalizacao-auto-de-infracao)

---

## ✨ Principais Funcionalidades

* **Pipeline de ETL Assíncrono (Crawler & Ingestion):** Um pipeline de dados completo, orquestrado via `cli.py`, que:
    1.  Baixa (crawls) o arquivo `.zip` de dados mais recente de forma assíncrona usando `httpx` (`CrawlerService`).
    2.  Processa os CSVs de grande volume em *chunks* (lotes) usando **Pandas**, garantindo baixo consumo de memória.
    3.  Ingere os dados no MySQL de forma assíncrona (`IngestionService`).
* **Operação de Upsert Inteligente:** A lógica de ingestão utiliza o `INSERT ... ON DUPLICATE KEY UPDATE` do MySQL (via `sqlalchemy.dialects.mysql.insert`), permitindo inserir novos registros e atualizar os existentes em uma única operação atômica, garantindo a consistência dos dados.
* **API RESTful 'Async-First':** Todos os endpoints são totalmente assíncronos (`async def`), desde a requisição web (FastAPI) até a consulta no banco de dados (SQLAlchemy 2.0 + `asyncmy`), garantindo altíssima concorrência e performance de I/O.
* **Autenticação Híbrida e Segura:** Sistema de segurança robusto que suporta **JWT (JSON Web Tokens)** para usuários (Roles: `ADMIN`, `USER`) e **API Keys** para acesso programático (machine-to-machine), com controle de acesso baseado em papéis (RBAC).
* **CI/CD e Automação na AWS:** Pipeline completo de Integração e Entrega Contínua **(GitHub Actions)** configurado para realizar linting, testes automatizados e deploy automático em instâncias **AWS EC2**.
* **Alta Performance com Redis:** Implementação de cache distribuído usando **Redis** para validação instantânea de API Keys, reduzindo drasticamente a latência e a carga no banco de dados relacional.
* **Configuração Moderna com Dynaconf:** Gerenciamento de configurações, usando `settings.toml` para padrões e `.secrets.toml` (git-ignored) para segredos e configurações de ambiente.
* **Ambiente Containerizado e Reprodutível:** O projeto é totalmente gerenciado pelo **Docker** e **Docker Compose**, orquestrando os containers da API, do banco de dados (MySQL) e do banco de testes. Contendo configuração de Docker Compose segregada (`docker-compose.prod.yml`) para ambientes produtivos, garantindo leveza e segurança.
* **Testes de Integração:** Suíte de testes automatizados usando `Pytest` e `httpx.AsyncClient`, que rodam contra um banco de dados de teste real e isolado para validar a API e a lógica de negócio.

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | Framework web de alta performance para construção de APIs assíncronas. |
| | **SQLAlchemy 2.0** | ORM para interação com o banco de dados, usando a nova sintaxe assíncrona (`AsyncSession`). |
| | **Pydantic V2** | Para validação, serialização de dados e gerenciamento de schemas da API. |
| | **Pandas** | Utilizado para o processamento eficiente (em *chunks*) de grandes arquivos CSV. |
| | **httpx** | Cliente HTTP assíncrono moderno, usado pelo Crawler para I/O de rede não-bloqueante. |
| | **Typer** | Para criação do `cli.py`, o ponto de entrada do pipeline de ETL. |
| **Banco de Dados & Cache** | **MySQL 8.0** | Banco de dados relacional principal. |
| | **asyncmy** | Driver MySQL assíncrono, permitindo o uso de `await` em queries. |
| | **Redis** | Armazenamento em memória chave-valor para cache de validação de credenciais.
| **Autenticação** | **JWT / Passlib** | Para geração de tokens de acesso seguros e hashing de senhas. |
| **Tooling & DevOps** | **Docker & Docker Compose** | Para containerização da aplicação, banco de dados e ambiente de testes. |
| | **GitHub Actions** | Automação de pipelines de CI (Lint/Test) e CD (Deploy AWS).
| | **AWS EC2** | Infraestrutura de nuvem para hospedagem da aplicação em produção.
| | **Alembic** | Ferramenta para gerenciamento de migrações de schema do banco de dados. |
| | **Dynaconf** | Gerenciador de configurações por ambiente. |
| | **Pytest** | Framework para testes de unidade e integração. |
| | **Uvicorn** | Servidor ASGI de alta performance para rodar a aplicação FastAPI. |

---

## 🚀 Como Executar o Projeto

O projeto é desenhado para ser executado **exclusivamente com Docker**. Não é necessário (nem recomendado) instalar dependências Python ou um banco de dados na sua máquina local.

### Pré-requisitos

* [**Docker**](https://www.docker.com/get-started) e [**Docker Compose**](https://docs.docker.com/compose/install/)
* (Recomendado) [VS Code](https://code.visualstudio.com/) com a extensão [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 1. Clonar o Repositório

```bash
git clone [https://github.com/luizvn/ibama_api.git](https://github.com/luizvn/ibama_api.git)
cd ibama_api
```

### 2. Configurar Variáveis de Ambiente

Este projeto usa o Docker Compose para injetar variáveis de ambiente no container da API a partir de um arquivo .env.
Crie um arquivo .env na raiz do projeto (este arquivo está no .gitignore e não será enviado ao repositório).

**Arquivo: .env**
```env
# Configurações do Banco de Dados (lidas pelo Docker Compose e pela API)
# Estas senhas devem bater com as do docker-compose.yml
DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASS=root
DB_NAME=ibama_db

# String de conexão principal (usada pela API e Alembic)
# Deve usar o driver 'asyncmy' e apontar para o nome do serviço 'db'
DATABASE_URL="mysql+asyncmy://root:root@db:3306/ibama_db"

# String de conexão de teste (usada pelo Pytest)
DATABASE_URL_TEST="mysql+asyncmy://root:root@db:3306/ibama_db_test"

# Chave secreta para assinar os tokens JWT
# Gere com: openssl rand -hex 32
SECRET_KEY="<sua_chave_secreta_de_32_bytes_aqui>"

# Configurações do Token JWT
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

PORT_API=80
```

### 3. Iniciar o Ambiente Docker

Este comando irá construir a imagem da API (se ainda não existir), iniciar o container da API e o container do banco de dados MySQL em segundo plano.

```bash
docker-compose up -d --build
```

Aguarde alguns segundos até que o banco de dados esteja totalmente inicializado (você pode verificar com docker-compose logs db).

### 4. Aplicar as Migrações do Banco de Dados

Com os containers em execução, execute o Alembic dentro do container da API para criar as tabelas no banco.

```bash
docker-compose exec api alembic upgrade head
```

### 5. Aplicar as Migrações do Banco de Dados
Com o banco de dados rodando e as dependências instaladas, aplique as migrações para criar as tabelas:
```bash
alembic upgrade head
```
### 5. Criar um Usuário Administrador

Para ter acesso aos endpoints administrativos (como o upload de CSV), você precisa de um usuário `ADMIN`.

**Passo 1: Crie um usuário via API**

Use a documentação interativa em `http://localhost:8000/docs` para enviar uma requisição `POST` para o endpoint `/users` ou utilize o comando `curl` abaixo no seu terminal.

```bash
curl -X POST "http://localhost:8000/users" \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "Test@1234"}'
```
**Passo 2: Promova o usuário para ADMIN**

Conecte-se ao seu banco de dados MySQL (usando DBeaver, DataGrip, ou o terminal do docker-compose) e execute o seguinte comando SQL para definir a `role` do usuário recém-criado como `ADMIN`.

```sql
UPDATE users SET role = 'ADMIN' WHERE username = 'admin';
```

### 6. Acessar a API

A API estará disponível em `http://localhost:8000`.
A documentação interativa (Swagger UI) pode ser acessada em `http://localhost:8000/docs`.

### 7. (Opcional) Executar o Pipeline de ETL Manualmente

Você pode disparar o pipeline completo de crawler e ingestão executando o `cli.py` *dentro* do container da API:

```bash
docker-compose exec api python cli.py run
```

Isso iniciará o download do arquivo .zip, processamento e ingestão no banco.

---

## 🏛️ Arquitetura e Decisões de Design

* **Estrutura de Projeto Limpa:** O código é organizado seguindo princípios de *separation of concerns*, dividindo a lógica em camadas de `api` (routers), `services` (lógica de negócio), `schemas` (contratos de dados Pydantic) e `models` (ORM SQLAlchemy).
* **Arquitetura 'Async-First':** A escolha por `async` de ponta-a-ponta (FastAPI, `httpx`, `asyncmy`) foi deliberada para maximizar a performance de I/O e a concorrência.
* **Cache Strategy (Redis):** Para evitar consultas repetitivas ao banco de dados na validação de API Keys (que ocorrem a cada requisição), implementamos uma camada de cache com Redis. Isso garante resposta em milissegundos e protege o banco de dados principal de picos de tráfego.
* **CI/CD e Deploy Automatizado:** A esteira de DevOps foi desenhada para garantir confiabilidade. O GitHub Actions executa testes e linters a cada commit, e realiza o deploy automático na AWS EC2 apenas se o pipeline for aprovado, utilizando segredos seguros e Docker em produção.
* **ETL como um Processo Separado (CLI):** O pipeline de ETL (`cli.py`) opera independentemente da API web, permitindo ingestão de grandes volumes de dados sem degradar a experiência do usuário final.
* **Configuração com Dynaconf:** O `Dynaconf` foi escolhido por sua flexibilidade, permitindo um sistema de configuração em camadas, onde `settings.toml` define padrões e variáveis de ambiente (lidas do `.env`) sobrescrevem com segredos.
* **Testes de Integração com Banco Real:** O `Pytest` (`conftest.py`) é configurado para rodar testes de integração contra um banco de dados de teste real (criado pelo `docker-compose` e `01-create-test-db.sql`). Isso garante que nossas queries e lógica de negócio funcionam como esperado no ambiente MySQL, indo além de mocks.

---

## 👨‍💻 Autor

**Luiz Vinícius Souza**

* [LinkedIn](https://www.linkedin.com/in/luizvn/)
* [GitHub](https://github.com/luizvn)
