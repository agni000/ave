import sqlite3
import os
from core.text_utils import make_preview

# Define caminho absoluto do banco SQLite dentro do projeto
# garante funcionamento independente do diretório de execução
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "ave.db")

# Garante que o diretório do banco exista antes de criar/conectar
os.makedirs(os.path.join(BASE_DIR, "db"), exist_ok=True)

# Cria conexão com o banco
def get_connection():
    # check_same_thread=False permite uso da conexão em múltiplas threads
    # necessário para integração com FastAPI
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
   
    # Habilita suporte a chaves estrangeiras no SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn  

# Inicializa esquema do banco (criação de tabelas)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de conversas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_message TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de mensagens
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )
    """)

    conn.commit()
    conn.close()

# Cria ou retorna o Id da conversa 
def get_or_create_conversation(conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cria a conversa somente se ela não existir ainda no banco 
    cursor.execute("""
        INSERT OR IGNORE INTO conversations (id, last_message, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (conversation_id, None))

    conn.commit()
    conn.close()

    return conversation_id

# Retorna um histórico recente de interações entre o usuário e assistente
def get_context(conversation_id, context_len):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Busca apenas as mensagens mais recentes (janela de contexto)
    # ordena desc para eficiência e depois reverte para ordem cronológica
    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (conversation_id, context_len))

    rows = cursor.fetchall()
    conn.close()
    
    # Reverte para ordem cronológica (modelo espera sequência correta) 
    rows.reverse()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]

# Salva mensagem
def save_message(conversation_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Persistencia no banco  
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
   
    # Gera preview reduzido para exibição no histórico
    content_preview = make_preview(content) 

    # atualiza metadados da conversa
    cursor.execute("""
        UPDATE conversations
        SET last_message = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (content_preview, conversation_id))
    
    conn.commit()
    conn.close()

# Retorna conversas ordenadas pela mais recente atualização
def get_conversations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, last_message, updated_at
        FROM conversations
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "last_message": row[1],
            "updated_at": row[2]
        }
        for row in rows
    ]

# Retorna todas as mensagens da conversa em ordem cronológica
def get_messages(conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    """, (conversation_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "role": row[0],
            "content": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]
