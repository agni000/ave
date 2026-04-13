import sqlite3
import os
from core.text_utils import make_preview

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "ave.db")

os.makedirs(os.path.join(BASE_DIR, "db"), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn  

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

def get_or_create_conversation(conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO conversations (id, last_message, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (conversation_id, None))

    conn.commit()
    conn.close()

    return conversation_id

def save_message(conversation_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    # salva mensagem 
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
   
    content_preview = make_preview(content) 

    # atualiza metadata da conversa
    cursor.execute("""
        UPDATE conversations
        SET last_message = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (content_preview, conversation_id))
    
    conn.commit()
    conn.close()

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
