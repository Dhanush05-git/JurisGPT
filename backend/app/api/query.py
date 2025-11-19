from fastapi import APIRouter
from app.services.retriever import Retriever
from app.services.llm_service import LLMService

router = APIRouter()

retriever = Retriever()
llm = LLMService()

@router.post("/")
async def process_query(payload: dict):
    query = payload.get("query", "")

    # Step 1: Retrieve relevant chunks
    results = retriever.search(query, k=3)

    # Combine chunks into context text
    context = "\n\n".join(results)

    # Step 2: LLM answer generation
    answer = llm.generate_answer(query, context)

    return {
        "query": query,
        "chunks_used": results,
        "answer": answer
    }
