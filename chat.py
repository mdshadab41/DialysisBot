"""
Chat Module
Combines retrieval with LLM to generate answers
"""

from groq import Groq # type: ignore
from typing import List, Dict
from retriever import Retriever
import config
from confidence import calculate_confidence

# Initialize Groq client once
client = Groq(api_key=config.GROQ_API_KEY)


class ChatBot:
    """
    Main chatbot that uses RAG to answer questions
    """

    def __init__(self):
        """Initialize chatbot with retriever"""
        self.retriever = Retriever()
        self.chat_history = []
        print("ChatBot initialized")

    def create_prompt(self, query: str, context: str) -> str:
        """
        Create prompt for the LLM

        Args:
            query: User's question
            context: Retrieved context from documents

        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful medical assistant specialized in dialysis care. 
Answer the user's question based ONLY on the context provided below. 

IMPORTANT RULES:
1. Only use information from the context
2. If the answer is not in the context, say "I don't have enough information to answer that question based on the available documents."
3. Be clear, concise, and accurate
4. Use medical terminology appropriately but explain complex terms
5. Always remind users to consult their healthcare provider for medical decisions

CONTEXT:
{context}

USER QUESTION: {query}

ANSWER:"""
        return prompt

    def chat(self, query: str, show_sources: bool = True) -> Dict:
        """
        Process a user query and generate response

        Args:
            query: User's question
            show_sources: Whether to return source information

        Returns:
            Dictionary with answer and sources
        """
        print(f"\n💬 User: {query}")

        # Step 1: Retrieve relevant chunks
        chunks = self.retriever.retrieve_with_scores(query, top_k=config.TOP_K)

        if not chunks:
            return {
                'answer': "I couldn't find relevant information in the documents. Please try rephrasing your question.",
                'sources': [],
                'confidence': {
                    'score': 0.0,
                    'level': 'No Data',
                    'explanation': 'No relevant information found'
                }
            }

        # Step 2: Format context
        context = self.retriever.format_context(chunks)

        # Step 3: Create prompt
        prompt = self.create_prompt(query, context)

        # Step 4: Generate answer with Groq
        print(f"🤖 Generating answer using {config.CHAT_MODEL} via Groq...")

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

            answer = response.choices[0].message.content

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            answer = "Sorry, I encountered an error while generating the response."

        # Prepare sources
        sources = []
        if show_sources:
            for chunk in chunks:
                metadata = chunk['metadata']
                sources.append({
                    'category': metadata['category'],
                    'filename': metadata['filename'],
                    'chunk_id': metadata['chunk_id'],
                    'similarity': chunk.get('similarity', 0),
                    'preview': chunk['text'][:200] + "..."
                })

        confidence = calculate_confidence(chunks)

        # Add to history
        self.chat_history.append({
            'query': query,
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        })

        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        }

    def display_response(self, response: Dict):
        """
        Display the chatbot response in a readable format
        """
        print("\n" + "="*70)
        print("🤖 CHATBOT RESPONSE")
        print("="*70)
        print(response['answer'])

        if response['sources']:
            print("\n" + "-"*70)
            print("📚 SOURCES:")
            print("-"*70)
            for i, source in enumerate(response['sources'], 1):
                print(f"\n[{i}] {source['category']}/{source['filename']}")
                print(f"    Similarity: {source['similarity']:.3f}")
                print(f"    Preview: {source['preview']}")

        print("="*70)


# Test the module if run directly
if __name__ == "__main__":
    print("Testing ChatBot with RAG...\n")
    print(config.DISCLAIMER)

    chatbot = ChatBot()

    test_questions = [
        "What foods should dialysis patients avoid?",
        "How does hemodialysis work?",
    ]

    for question in test_questions:
        print("\n" + "="*70)
        response = chatbot.chat(question, show_sources=True)
        chatbot.display_response(response)
        input("\nPress Enter to continue...")