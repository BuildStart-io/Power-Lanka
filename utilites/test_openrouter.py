import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

from app.services.rag_service import RAGService
from app.config import get_settings

def test_openrouter():
    settings = get_settings()
    print(f"Testing OpenRouter with model: {settings.openrouter_model}")
    
    try:
        service = RAGService()
        result = service.generate_response("Test connection")
        
        print("\n✅ OpenRouter Success!")
        print("Response:", result["response"])
        
    except Exception as e:
        print("\n❌ OpenRouter Failed")
        print(str(e))

if __name__ == "__main__":
    test_openrouter()
