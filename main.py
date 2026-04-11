from fastapi import FastAPI
from routes.chat import router as chat_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# routes
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
