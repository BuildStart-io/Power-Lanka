import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the backend directory is in the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
# Try to find .env file in parent directory if not in current
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from app.services.rag_service import RAGService

async def main():
    print("Initializing RAG Service...")
    try:
        rag_service = RAGService()
        print("RAG Service Initialized. Ready to chat! (Type 'quit' or 'exit' to stop)")
    except Exception as e:
        print(f"Error initializing RAG Service: {e}")
        return

    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            print("Bot is thinking...", end="", flush=True)
            
            # Since RAGService.generate_response is synchronous (based on my reading of the file)
            # We can call it directly. If it were async, we'd await it.
            # Looking at rag_service.py validation, it seems synchronous:
            # def generate_response(self, query: str, conversation_history: Optional[list[dict]] = None, ...)
            
            response_data = rag_service.generate_response(
                query=user_input,
                conversation_history=conversation_history
            )
            
            response_text = response_data.get("response", "")
            
            # Clear "Bot is thinking..." line
            print("\r" + " " * 20 + "\r", end="", flush=True)
            
            print(f"Bot: {response_text}")

            # Update history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response_text})

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
