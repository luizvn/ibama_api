# API de Autos de Infração Ambiental - IBAMA

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.117-blue?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-blue?logo=sqlalchemy)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)

## 🇧🇷 Sobre o Projeto

A **API IBAMA** é uma solução de backend robusta e de alta performance, projetada para a ingestão e consulta de dados públicos sobre autos de infração ambiental emitidos pelo IBAMA. O principal desafio deste projeto é o processamento eficiente de arquivos CSV de múltiplos gigabytes, garantindo que os dados sejam validados, processados e armazenados de forma assíncrona, sem impactar a disponibilidade da API.

Este projeto foi construído utilizando as mais modernas ferramentas do ecossistema Python, com foco em boas práticas de desenvolvimento, escalabilidade e manutenibilidade.

---

## 🗃️ Fonte dos Dados

A API consome os dados públicos de autos de infração e sanções ambientais, que são abertamente disponibilizados pelo IBAMA através do Portal de Dados Abertos do Governo Federal.

Os conjuntos de dados originais, em formato CSV, que servem de insumo para a funcionalidade de ingestão desta API podem ser encontrados e baixados no seguinte link:

* **Link Oficial:** [**Fiscalização - Auto de Infração**](https://dados.gov.br/dados/conjuntos-dados/fiscalizacao-auto-de-infracao)

---

## ✨ Principais Funcionalidades

* **Ingestão de Dados em Larga Escala:** Endpoint otimizado para receber arquivos CSV de grande volume. O processamento é feito em *background* (assíncrono), utilizando **Pandas** para leitura em *chunks*, o que garante um baixo consumo de memória e alta performance.
* **Operação de Upsert Inteligente:** A lógica de ingestão utiliza o `INSERT ... ON DUPLICATE KEY UPDATE` do MySQL, permitindo inserir novos registros e atualizar os existentes em uma única operação atômica, garantindo a consistência dos dados.
* **Autenticação e Autorização Segura:** Implementação de autenticação baseada em tokens **JWT (JSON Web Tokens)** e um sistema de autorização baseado em papéis (Roles: `ADMIN`, `USER`), garantindo que apenas usuários autorizados possam acessar determinados recursos.
* **API de Consulta Avançada:** Endpoints RESTful para consulta de infrações com múltiplos filtros combináveis (data, valor da multa, infrator, localização, etc.) e sistema de paginação.
* **Gerenciamento de Migrações de Banco de Dados:** Utilização do **Alembic** para versionar o schema do banco de dados de forma segura e reprodutível.
* **Ambiente Containerizado:** O projeto é totalmente containerizado com **Docker** e **Docker Compose**, facilitando a configuração do ambiente de desenvolvimento e garantindo consistência entre diferentes máquinas.

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | Framework web de alta performance para construção de APIs com Python moderno. |
| | **SQLAlchemy 2.0** | ORM para interação com o banco de dados, utilizando a nova sintaxe declarativa e `select()`. |
| | **Pydantic V2** | Para validação e serialização de dados, garantindo a integridade dos dados na camada de API. |
| | **Pandas** | Utilizado para o processamento eficiente e em memória de grandes arquivos CSV. |
| **Banco de Dados** | **MySQL 8.0** | Banco de dados relacional para armazenamento dos dados das infrações. |
| **Autenticação** | **JWT / Passlib** | Para geração de tokens de acesso seguros e hashing de senhas. |
| **Tooling & DevOps** | **Docker & Docker Compose** | Para containerização da aplicação e do banco de dados. |
| | **Alembic** | Ferramenta para gerenciamento de migrações de schema do banco de dados. |
| | **Uvicorn** | Servidor ASGI de alta performance para rodar a aplicação FastAPI. |

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

* [**Docker**](https://www.docker.com/get-started) e [**Docker Compose**](https://docs.docker.com/compose/install/)
* [**Python 3.11+**](https://www.python.org/downloads/)
* Gerenciador de pacotes `pip` e `venv`

### 1. Clonar o Repositório

```bash
git clone [https://github.com/luizvn/ibama_api.git](https://github.com/luizvn/ibama_api.git)
cd ibama_api
```
### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto, usando o modelo abaixo. Este arquivo conterá as configurações sensíveis da aplicação.

**Arquivo: `.env`**
```env
# Configurações do Banco de Dados
DATABASE_URL="mysql+pymysql://root:root@localhost:3306/ibama_db"

# Configurações de Segurança do JWT
SECRET_KEY="<gere_uma_chave_secreta_aqui_ex: openssl rand -hex 32>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
### 3. Iniciar o Banco de Dados com Docker

Com o Docker em execução, suba o container do MySQL:
```bash
docker-compose up -d
```
Entendido. O texto que você colou está com a formatação do Markdown quebrada. Vou reconstruir essa seção para você.

Aqui está o trecho, começando de "Aguarde alguns segundos..." até o final da seção de instalação, com a formatação correta em Markdown (raw).

Markdown

Aguarde alguns segundos até que o banco de dados esteja totalmente inicializado.

### 4. Configurar o Ambiente Python e Instalar Dependências

Crie e ative um ambiente virtual:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```
Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```
### 5. Aplicar as Migrações do Banco de Dados
Com o banco de dados rodando e as dependências instaladas, aplique as migrações para criar as tabelas:
```bash
alembic upgrade head
```
### 6. Criar um Usuário Administrador

Para ter acesso aos endpoints administrativos, primeiro crie um usuário comum através da API e depois altere sua permissão (`role`) diretamente no banco de dados.

**Passo 1: Crie um usuário via API**

Use a documentação interativa em `http://localhost:8000/docs` para enviar uma requisição `POST` para o endpoint `/users` ou utilize o comando `curl` abaixo no seu terminal.

```bash
curl -X POST "http://localhost:8000/users" \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "seu-password-aqui"}'
```
**Passo 2: Promova o usuário para ADMIN**

Conecte-se ao seu banco de dados MySQL (usando DBeaver, DataGrip, ou o terminal) e execute o seguinte comando SQL para definir a `role` do usuário recém-criado como `ADMIN`.

```sql
UPDATE users SET role = 'ADMIN' WHERE username = 'admin';
```
### 7. Iniciar a Aplicação
Finalmente, inicie o servidor da API com Uvicorn:
```bash
uvicorn app.main:app --reload
```
A API estará disponível em `http://localhost:8000`. A documentação interativa (Swagger UI) pode ser acessada em `http://localhost:8000/docs`.

---

## 🏛️ Arquitetura e Decisões de Design

* **Estrutura de Projeto Limpa:** O código é organizado seguindo princípios de *separation of concerns*, dividindo a lógica em camadas de `api` (routers), `services` (lógica de negócio), `schemas` (contratos de dados Pydantic) e `models` (ORM SQLAlchemy).
* **Injeção de Dependências:** O sistema de injeção de dependências do FastAPI (`Depends`) é utilizado extensivamente para gerenciar sessões de banco de dados e a autenticação de usuários, promovendo um código desacoplado e fácil de testar.
* **SQLAlchemy 2.0 (Sintaxe Moderna):** A escolha pela sintaxe da versão 2.0, baseada em `select()`, foi feita por ser mais explícita, poderosa e alinhada com a forma como o SQL funciona, em contraste com a API de `query()` mais antiga.
* **Processamento Assíncrono para I/O Bound:** A ingestão do CSV é uma tarefa *I/O-bound* (limitada pela leitura do disco e escrita no banco). O uso de `BackgroundTasks` do FastAPI permite que essas operações longas não bloqueiem o *event loop* principal, mantendo a API responsiva para outras requisições.

---

## 👨‍💻 Autor

**Luiz Vinícius Souza**

* [LinkedIn](https://www.linkedin.com/in/luizvn/)
* [GitHub](https://github.com/luizvn)
