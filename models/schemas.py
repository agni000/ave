from pydantic import BaseModel

# Modelo de requisição para envio de mensagens no chat. 
class ChatRequest(BaseModel):
    message: str
    conversation_id: str 
