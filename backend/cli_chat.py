import os
import sys
import uvicorn
import requests
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

# Configure Logging to see internal tool logs
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Auto-seed if needed
        from seed_data import seed_products
        try:
            seed_products()
        except Exception as seed_err:
            print(f"Seeding ignored or failed: {seed_err}")

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

class Key(BaseModel):
    cleanedSenderPn: str

class MessageItem(BaseModel):
    key: Key
    messageBody: str

class DataPayload(BaseModel):
    messages: MessageItem

class WebhookPayload(BaseModel):
    event: str
    data: DataPayload

@app.post("/chat")
async def chat_endpoint(payload: WebhookPayload):
    """
    Simulates the webhook endpoint.
    Expects complex JSON structure from WhatsApp gateway.
    """
    global rag_service
    if not rag_service:
        return {"error": "RAG Service not initialized"}
    
    # Extract data from nested structure
    try:
        from_number = payload.data.messages.key.cleanedSenderPn
        message_body = payload.data.messages.messageBody
    except AttributeError:
        return {"error": "Invalid payload structure"}

    print(f"\n[POST] Received from {from_number}: {message_body}")
    
    # RAG Service expects conversation history.
    # For this simple CLI/Test server, we might not maintain history per user 
    # unless we implement a simple dict memory, or just pass empty history.
    # The real app uses the DB for history.
    
    # We will pass empty history for now to test single-turn RAG, 
    # or we could attempt to fetch from DB if we imported the DB logic.
    # Let's keep it simple: no memory for this test server.
    
    response_data = rag_service.generate_response(
        query=message_body,
        conversation_history=[], # Stateless for this test
        phone_number=from_number
    )
    
    response_text = response_data.get("response", "")
    response_text = response_data.get("response", "")
    print(f"[RESP] Bot: {response_text}")

    # Send response to WhatsApp via WASender API
    wa_api_url = "https://wasenderapi.com/api/send-message"
    wa_token = os.getenv("WASENDER_TOKEN")
    
    if not wa_token:
        print("WASENDER_TOKEN not found in environment variables.")
        return {
            "response": response_text,
            "request_body": message_body,
            "error": "WASENDER_TOKEN missing"
        }
    
    headers = {
        "Authorization": f"Bearer {wa_token}",
        "Content-Type": "application/json"
    }
    
    # Ensure phone number has '+' prefix
    formatted_number = from_number if from_number.startswith("+") else f"+{from_number}"

    json_data = {
        "to": formatted_number,
        "text": response_text
    }
    
    try:
        print(f"Sending response to {from_number} via WASender...")
        wa_response = requests.post(wa_api_url, headers=headers, json=json_data)
        print(f"WASender Response: {wa_response.status_code} - {wa_response.text}")
    except Exception as e:
        print(f"Failed to send to WASender: {e}")
    
    return {
        "response": response_text,
        "request_body": message_body
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting Setup Server on port 8000...")
    print("Swagger Docs available at: http://localhost:8000/docs")
    print("Send POST requests to: http://localhost:8000/chat")
    # Run on 8000 to match docker-compose configuration
    uvicorn.run(app, host="0.0.0.0", port=8000)
