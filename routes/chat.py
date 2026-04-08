from fastapi import APIRouter
from models.schemas import ChatRequest
from services.llm import generate_response
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
def root():
    return FileResponse("static/index.html")

@router.post("/")
def chat(req: ChatRequest):
    reply = generate_response(req.message)
    return {"response": reply}
