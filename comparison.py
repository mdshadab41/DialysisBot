"""
RAG vs Non-RAG Comparison Module
Compare answers with and without retrieval
"""

from groq import Groq # type: ignore
from chat import ChatBot
import config

# Initialize Groq client once
client = Groq(api_key=config.GROQ_API_KEY)

git lfs track "*.pdf"


class Comparator:
    """
    Compare RAG vs Non-RAG responses
    """

    def __init__(self):
        """Initialize with chatbot"""
        self.chatbot = ChatBot()
        print("✅ Comparator initialized")

    def get_non_rag_response(self, query: str) -> str:
        """
        Get response without RAG (just LLM)

        Args:
            query: User's question

        Returns:
            Answer from LLM without retrieval
        """
        prompt = f"""You are a helpful medical assistant specialized in dialysis care.
Answer the following question based on your general knowledge:

Question: {query}

Answer:"""

        try:
            response = client.chat.completions.create(
                model=config.CHAT_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful medical assistant for dialysis patients.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=config.TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    def compare(self, query: str) -> dict:
        """
        Compare RAG vs Non-RAG responses

        Args:
            query: User's question

        Returns:
            Dictionary with both responses and metadata
        """
        print(f"\n🔄 Comparing responses for: '{query}'")

        # Get RAG response
        print("1️⃣ Getting RAG response...")
        rag_response = self.chatbot.chat(query, show_sources=True)

        # Get Non-RAG response
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


# Test the module
if __name__ == "__main__":
    print("Testing RAG vs Non-RAG Comparison...\n")

    comparator = Comparator()
    test_query = "What foods should dialysis patients avoid?"
    result = comparator.compare(test_query)

    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    print(f"\nQuestion: {result['query']}")

    print("\n--- WITH RAG (Using PDFs) ---")
    print(result['rag']['answer'])
    print(f"\nConfidence: {result['rag']['confidence']['score']}%")
    print(f"Sources: {len(result['rag']['sources'])} documents")

    print("\n--- WITHOUT RAG (Just LLM) ---")
    print(result['non_rag']['answer'])
    print("\n" + "="*70)