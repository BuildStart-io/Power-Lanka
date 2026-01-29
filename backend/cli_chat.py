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
from app.database import SessionLocal, WhatsAppSession, ConversationMessage
import uuid
from datetime import datetime

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
    
    # Initialize DB Session
    db = SessionLocal()
    response_text = ""
    try:
        # Standardize phone number for lookup
        lookup_number = from_number.strip()
        
        # Get or create WhatsApp session
        wa_session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == lookup_number).first()
        
        if not wa_session:
            print(f"[DB] Creating NEW session for {lookup_number}")
            wa_session = WhatsAppSession(
                id=str(uuid.uuid4()),
                phone_number=lookup_number,
                session_id=str(uuid.uuid4()),
            )
            db.add(wa_session)
            db.commit()
            db.refresh(wa_session)
        else:
            print(f"[DB] Found EXISTING session: {wa_session.session_id}")
        
        # Update last message time
        wa_session.last_message_at = datetime.utcnow()
        db.commit()

        # Get conversation history
        history_msgs = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == wa_session.session_id
        ).order_by(ConversationMessage.created_at.asc()).all()
        
        print(f"[DB] Loaded {len(history_msgs)} history messages")
        
        conversation_history = [{"role": m.role, "content": m.content} for m in history_msgs]
        
        # Generate Response
        # Note: rag_service tools (add_to_cart) create their own DB storage. 
        # They need the correct phone number to look up this SAME session.
        response_data = rag_service.generate_response(
            query=message_body,
            conversation_history=conversation_history,
            phone_number=lookup_number
        )
        
        response_text = response_data.get("response", "")
        print(f"[RESP] Bot: {response_text}")
        
        # Save messages to DB
        user_msg = ConversationMessage(
            id=str(uuid.uuid4()),
            session_id=wa_session.session_id,
            role="user",
            content=message_body
        )
        db.add(user_msg)
        
        assistant_msg = ConversationMessage(
            id=str(uuid.uuid4()),
            session_id=wa_session.session_id,
            role="assistant",
            content=response_text
        )
        db.add(assistant_msg)
        db.commit()
        print("[DB] Saved chat messages committed.")

    except Exception as e:
        print(f"Database Error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback if DB fails
        response_data = rag_service.generate_response(
            query=message_body,
            conversation_history=[],
            phone_number=from_number
        )
        response_text = response_data.get("response", "")
    finally:
        db.close()

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
