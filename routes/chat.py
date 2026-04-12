from fastapi import APIRouter
from models.schemas import ChatRequest
from services.llm import generate_response
from fastapi.responses import FileResponse
from db.database import save_message, get_or_create_conversation, get_connection
import os 

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_PATH = os.path.join(BASE_DIR, "static", "index.html")

@router.get("/")
def root():
    return FileResponse(UI_PATH)


@router.get("/historico")
def get_historico():
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

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
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

@router.post("/")
def chat(req: ChatRequest):
    conversation_id = req.conversation_id 

    get_or_create_conversation(conversation_id)

    # salva mensagem do usuário primeiro 
    save_message(conversation_id, "user", req.message)

    result = generate_response(req.message)

    if not result["error"]:
        save_message(conversation_id, "assistant", result["response"])

    return result
