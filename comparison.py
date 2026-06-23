"""
RAG vs Non-RAG Comparison Module
Compare answers with and without retrieval
"""

import requests
from chat import ChatBot
import config


class Comparator:
    """
    Compare RAG vs Non-RAG responses
    """

    def __init__(self):
        self.chatbot = ChatBot()
        print("✅ Comparator initialized")

    def get_non_rag_response(self, query: str) -> str:
        prompt = f"""You are a helpful medical assistant specialized in dialysis care.
Answer the following question based on your general knowledge:

Question: {query}

Answer:"""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.CHAT_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful medical assistant for dialysis patients."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": config.TEMPERATURE
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"API Error {response.status_code}: {response.text[:200]}"

        except Exception as e:
            return f"Error: {str(e)}"

    def compare(self, query: str) -> dict:
        print(f"\n🔄 Comparing responses for: '{query}'")

        print("1️⃣ Getting RAG response...")
        rag_response = self.chatbot.chat(query, show_sources=True)

        print("2️⃣ Getting Non-RAG response...")
        non_rag_answer = self.get_non_rag_response(query)

        return {
            'query': query,
            'rag': {
                'answer': rag_response['answer'],
                'sources': rag_response.get('sources', []),
                'confidence': rag_response.get('confidence', {})
            },
            'non_rag': {
                'answer': non_rag_answer,
                'sources': [],
                'confidence': {
                    'score': 0,
                    'level': 'N/A',
                    'explanation': 'No retrieval used'
                }
            }
        }