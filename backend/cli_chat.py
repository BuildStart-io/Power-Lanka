import os
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from app.services.rag_service import RAGService

from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse

# Initialize Service
# Global instance to avoid re-init on every request if expensive
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service
    print("Initializing RAG Service...")
    try:
        rag_service = RAGService()
        print("RAG Service Initialized!")
    except Exception as e:
        print(f"Failed to initialize RAG Service: {e}")
    yield
    # Clean up if needed
    print("Shutting down RAG Service...")

# Create FastAPI app
app = FastAPI(title="CLI Chat Server", lifespan=lifespan)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

class WebhookPayload(BaseModel):
    fromNumber: str
    body: str

@app.post("/chat")
async def chat_endpoint(payload: WebhookPayload):
    """
    Simulates the webhook endpoint.
    Expects JSON: { "fromNumber": "...", "body": "..." }
    """
    global rag_service
    if not rag_service:
        return {"error": "RAG Service not initialized"}
    
    print(f"\n[POST] Received from {payload.fromNumber}: {payload.body}")
    
    # RAG Service expects conversation history.
    # For this simple CLI/Test server, we might not maintain history per user 
    # unless we implement a simple dict memory, or just pass empty history.
    # The real app uses the DB for history.
    
    # We will pass empty history for now to test single-turn RAG, 
    # or we could attempt to fetch from DB if we imported the DB logic.
    # Let's keep it simple: no memory for this test server.
    
    response_data = rag_service.generate_response(
        query=payload.body,
        conversation_history=[], # Stateless for this test
        phone_number=payload.fromNumber
    )
    
    response_text = response_data.get("response", "")
    print(f"[RESP] Bot: {response_text}")
    
    return {
        "response": response_text,
        "request_body": payload.body
    }

if __name__ == "__main__":
    print("Starting Setup Server on port 8001...")
    print("Swagger Docs available at: http://localhost:8001/docs")
    print("Send POST requests to: http://localhost:8001/chat")
    # Run on 8001 to avoid modifying the main app port logic
    uvicorn.run(app, host="0.0.0.0", port=8001)
