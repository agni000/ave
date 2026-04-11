import sqlite3
import uuid
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "ave.db")

os.makedirs(os.path.join(BASE_DIR, "db"), exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de conversas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

def create_conversation():
    conn = get_connection()
    cursor = conn.cursor()

    conversation_id = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO conversations (id) VALUES (?)",
        (conversation_id,)
    )

    conn.commit()
    conn.close()

    return conversation_id

def get_or_create_conversation(conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO conversations (id)
        VALUES (?)
    """, (conversation_id,))

    conn.commit()
    conn.close()

def save_message(conversation_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )

    conn.commit()
    conn.close()


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
