from fastapi import APIRouter
from models.schemas import ChatRequest
from services.llm import generate_response
from fastapi.responses import FileResponse
from db.database import save_message, get_or_create_conversation, get_connection, get_messages, get_conversations  
import os 

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_PATH = os.path.join(BASE_DIR, "static", "index.html")

@router.get("/")
def root():
    return FileResponse(UI_PATH)

@router.get("/historico")
def get_historico():
    return get_conversations()

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    return get_messages(conversation_id)

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
