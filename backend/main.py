from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as learning_router
from auth.routes import auth_router
from database.connection import init_database


app = FastAPI(
    title="Agentic Learning System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://study-ai-u852.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_database()

app.include_router(auth_router)
app.include_router(learning_router)


@app.get("/")
def root():
    return {
        "message": "Agentic Learning System API is running"
    }