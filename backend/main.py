from fastapi import FastAPI
import uvicorn
from backend.api.router import chat_router


app = FastAPI(title="Deep Researcher API")
app.include_router(chat_router, prefix="/api")
