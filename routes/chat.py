from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest
from services.llm import generate_response
from fastapi.responses import FileResponse
from db.database import save_message, get_or_create_conversation, get_messages, get_conversations, get_context  
import os 

router = APIRouter()

# Resolve caminho absoluto até a raiz do projeto
# necessário para servir arquivos estáticos corretamente via FastAPI
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_PATH = os.path.join(BASE_DIR, "static", "index.html")

# Serve a interface web principal (SPA)
@router.get("/")
def root():
    return FileResponse(UI_PATH)

# Retorna lista de conversas ordenadas por atualização recente
@router.get("/conversations")
def get_history():
    return get_conversations()

# Retorna todas as mensagens de uma conversa específica
@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    return get_messages(conversation_id)

# Endpoint principal do chat:
# - garante existência da conversa
# - salva mensagem do usuário
# - recupera contexto recente
# - envia requisição ao modelo
# - salva resposta do assistente
@router.post("/")
def chat(req: ChatRequest):
    conversation_id = req.conversation_id 

    get_or_create_conversation(conversation_id)

    # salva mensagem do usuário primeiro 
    save_message(conversation_id, "user", req.message)

    # Recupera as últimas N mensagens para manter contexto da conversa
    # evita enviar histórico completo (limitação de tokens/performance) 
    context = get_context(conversation_id, 12)
    
    # envia a mensagem e o contexto para o modelo 
    result = generate_response(context)

    if result["error"]:
        raise HTTPException(
        status_code=500,
        detail=result["message"]
    )

    save_message(conversation_id, "assistant", result["response"])

    return {
        "response": result["response"]
    }

