# backend/app/services/llm_service.py
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
except Exception:
    Groq = None

API_KEY = os.getenv("GROQ_API_KEY")

class LLMService:
    def __init__(self):
        if Groq is None or API_KEY is None:
            self.client = None
        else:
            self.client = Groq(api_key=API_KEY)

    def generate_answer(self, query: str, context: str) -> str:
        """
        Ask model to respond in the JurisGPT structure:
        1) Summary (2-3 lines)
        2) Relevant Legal Provisions (act, sections, short quotes)
        3) Case Law (if present in context)
        4) Step-by-step explanation
        5) Safety Note
        IMPORTANT: Model must ONLY use the provided context and must NOT hallucinate.
        """
        prompt = f"""
You are JurisGPT, an assistant specialized in Indian law.

INSTRUCTIONS:
- Use ONLY the provided CONTEXT. Do NOT invent laws, sections, or cases.
- If the context does not contain the information needed, respond exactly:
  "The relevant information is not available in the provided documents."
- Output MUST be structured exactly as:
  1) Summary (2-3 lines)
  2) Relevant Legal Provisions:
     - <Act Name> — Section <x>: "<short quote or excerpt from context>"
     - ...
  3) Case Law:
     - <Case name / citation and short excerpt> (only if present in context)
  4) Step-by-step explanation:
     - <clear numbered steps explaining how the law applies, based only on context>
  5) Safety Note: "This is for informational purposes only and not legal advice."

QUESTION:
{query}

CONTEXT:
{context}

Produce the answer now using only the context and the structure above.
"""

        if self.client is None:
            # fallback: return context-aware fixed message
            return "LLM client not configured. Please set GROQ_API_KEY and ensure the groq package is installed."

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            # Groq SDK returns response.choices[0].message.content
            text = response.choices[0].message.content
            return text
        except Exception as e:
            # return readable error for debugging
            return f"LLM generation error: {str(e)}"
