from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.query import router as query_router

app = FastAPI(
    title="JurisGPT Backend",
    description="FastAPI backend for RAG-based legal query processing",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; we will restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api/query", tags=["Query"])

@app.get("/")
def root():
    return {"message": "JurisGPT Backend Running!"}
