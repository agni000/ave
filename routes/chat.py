from fastapi import APIRouter
from models.schemas import ChatRequest
from services.llm import generate_response
from fastapi.responses import FileResponse
from db.database import save_message, get_or_create_conversation, get_connection

router = APIRouter()

@router.get("/")
def root():
    return FileResponse("static/index.html")

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
