import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate_answer(self, query: str, context: str):
        prompt = f"""
                You are JurisGPT, an AI specialized in Indian law.

                Answer ONLY using the provided context.
                Do NOT invent or hallucinate any law, section or article.

            Question:
            {query}

            Context:
            {context}

            Provide a clear, concise legal explanation:
            """

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
