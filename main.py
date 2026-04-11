from fastapi import FastAPI
from routes.chat import router as chat_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db 

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

# configs
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(chat_router)


