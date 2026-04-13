# ave

Chatbot de **tutoria em química** desenvolvido no contexto de disciplina acadêmica de Inteligência Artificial I: backend em **FastAPI**, persistência em **SQLite** (conversas e mensagens) e **interface web** em página única que consome a API do modelo [ministral-14b-instruct-2512](https://build.nvidia.com/mistralai/ministral-14b-instruct-2512). O assistente responde em **português** e mantém o foco em tópicos de química.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Início rápido](#início-rápido)
- [Executando a aplicação](#executando-a-aplicação)
- [Referência da API](#referência-da-api)
- [Armazenamento de dados](#armazenamento-de-dados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Limitações](#limitações) 

---

## Funcionalidades

- Interface de chat com renderização Markdown (via CDN do [marked](https://github.com/markedjs/marked)).
- Lista de conversas (“Histórico”) persistida no SQLite.
- Fluxo de nova conversa com IDs gerados no cliente (`crypto.randomUUID()`).
- Visualização de conversas antigas pela sidebar.
- Janela recente de mensagens enviada ao LLM no servidor, o contexto é obtido através de uma query no banco e é adaptado à conversa atual.

---

## Arquitetura

```mermaid
flowchart LR
  Browser["Interface"]
  FastAPI["Servidor"]
  SQLite[("SQLite ave.db")]
  Model["mistralai/ministral-14b-instruct-2512"]

  Browser -->|"HTTP JSON"| FastAPI
  FastAPI --> SQLite
  FastAPI -->|HTTPS| Model
```

1. O navegador carrega `GET /` (arquivo `static/index.html`).
2. `POST /` envia a mensagem do usuário e o `conversation_id`; a API grava as mensagens e chama o modelo.
3. O histórico usa `GET /conversations` e `GET /conversations/{id}/messages`.

---

## Requisitos

- **Python 3.10+** (recomendado; compatível com as versões atuais de FastAPI/Pydantic).
- Uma **chave de API da NVIDIA** com acesso ao modelo ministral-14b-instruct-2512.

---

## Início rápido

### 1. Clonar o repositório 

```bash
git clone https://github.com/agni000/ave.git
cd ave
```

### 2. Criar e ativar um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
# venv\Scripts\activate    # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de ambiente

Crie um arquivo `.env` na **raiz do projeto** (mesmo diretório que `main.py`).

```env
NVIDIA_API_KEY=sua_chave_nvidia_aqui
```

Obtenha a chave [aqui](https://build.nvidia.com/mistralai/ministral-14b-instruct-2512).

---

## Executando a aplicação

Inicie o **Uvicorn a partir da raiz do repositório** para que `StaticFiles(directory="static")` resolva os caminhos corretamente:

```bash
uvicorn main:app --reload --port 8000
```

Em seguida abra **http://127.0.0.1:8000/** no navegador.

---

## Referência da API

URL base (localhost): `http://127.0.0.1:8000`

### `GET /`

Retorna a página **HTML** do chat (`static/index.html`).

---

### `POST /`

Envia uma mensagem de chat para uma conversa.

**Corpo da requisição** (`application/json`):

| Campo              | Tipo   | Descrição                                      |
|--------------------|--------|------------------------------------------------|
| `message`          | string | Texto da mensagem do usuário.                  |
| `conversation_id`  | string | UUID ou identificador estável do tópico.       |

**Resposta de sucesso** (`200`, JSON):

```json
{ 
  "response": "Resposta do assistente em português."
}
```

**Resposta de erro** (`500`, JSON):

```json
{
  "detail": "Erro legível (ex.: tempo esgotado, erro HTTP)."
}
```

A mensagem do usuário é sempre salva; a resposta do assistente só é salva quando `error` é `false`.

---

### `GET /conversations`

Lista as conversas, da mais recente para a mais antiga ao lado do chat principal.

**Resposta:** array JSON de objetos:

```json
[
  {
    "id": "string-uuid",
    "last_message": "Prévia do texto…",
    "updated_at": "data/hora no estilo SQLite"
  }
]
```

---

### `GET /conversations/{conversation_id}/messages`

Mensagens de uma conversa, da mais antiga para a mais recente.

**Resposta:** array JSON:

```json
[
  {
    "role": "user",
    "content": "…",
    "created_at": "…"
  }
]
```

---

## Armazenamento de dados

* **Arquivo do banco:** `db/ave.db` (criado na primeira subida do servidor via `init_db()`).

### conversations

| Campo          | Tipo     | Descrição                              |
| -------------- | -------- | -------------------------------------- |
| `id`           | TEXT     | Identificador único da conversa (UUID) |
| `created_at`   | DATETIME | Data de criação da conversa            |
| `last_message` | TEXT     | Prévia da última mensagem              |
| `updated_at`   | DATETIME | Data da última atualização             |

---

### messages

| Campo             | Tipo     | Descrição                                 |
| ----------------- | -------- | ----------------------------------------- |
| `id`              | INTEGER  | Identificador único (autoincremento)      |
| `conversation_id` | TEXT     | ID da conversa associada                  |
| `role`            | TEXT     | Papel da mensagem (`user` ou `assistant`) |
| `content`         | TEXT     | Conteúdo da mensagem                      |
| `created_at`      | DATETIME | Data de criação da mensagem               |

---

## Estrutura do projeto

```
ave/
├── main.py              # Entry-point  
├── requirements.txt
├── .env                 # precisa ser criado depois de clonar o repo  
├── core/
│   ├── config.py        # ambiente / NVIDIA_API_KEY
│   └── text_utils.py    # utilitários que melhoram o preview de textos no histórico 
├── db/
│   ├── database.py      # SQLite, esquema, helpers de persistência
│   └── ave.db           # gerado em tempo de execução 
├── models/
│   └── schemas.py       # modelo simples para as requisições 
├── routes/
│   └── chat.py          # rotas HTTP: UI, chat, histórico
├── services/
│   └── llm.py           # cliente NVIDIA + histórico em memória
└── static/
    ├── index.html       # UI do chat
    └── styles.css       # estilos da interface
```

## Limitações

 - Apenas uma janela recente de mensagens é enviada ao modelo (context window limitada). 
  Isso significa que, em conversas muito longas, partes antigas podem não ser consideradas na geração de respostas.
