from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from ..database import get_db, ConversationMessage, WhatsAppSession, get_sl_time
from ..services import RAGService
from ..services.wasender_service import send_wasender_message_background
from ..models import WhatsAppMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/webhook")
async def handle_wasender_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle incoming WhatsApp messages from WASender webhook.
    
    Compatible with both legacy and new WASender payload formats.
    """
    try:
        payload = await request.json()
        
        # Extract user ID (phone number) and message
        user_id = None
        message_text = None
        
        # Try legacy format
        if "fromNumber" in payload:
            user_id = payload.get("fromNumber")
            message_text = payload.get("message") or payload.get("body")
            
        # Try WhatsApp-style format
        elif "data" in payload:
            msg_data = payload.get("data", {}).get("messages", {})
            # senderPn or cleanedSenderPn
            key_data = msg_data.get("key", {})
            user_id = key_data.get("cleanedSenderPn") or key_data.get("senderPn")
            
            # Message body
            message_text = msg_data.get("messageBody") or \
                          msg_data.get("message", {}).get("extendedTextMessage", {}).get("text")
        
        if not user_id or not message_text:
            logger.warning(f"[Webhook] Invalid payload structure: {payload}")
            return {"status": "ignored", "reason": "missing_fields"}
            
        # Standardize phone number
        phone_number = str(user_id).strip()
        message = str(message_text).strip()
        
        logger.info(f"[Webhook] Received message from {phone_number}: {message[:50]}...")
        
        # Process message properly
        return await process_message_internal(phone_number, message, db, background_tasks)
        
    except Exception as e:
        logger.error(f"[Webhook] Error processing webhook: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def process_message_internal(
    phone_number: str, 
    message: str, 
    db: Session,
    background_tasks: BackgroundTasks
):
    """
    Internal logic to process message and generate response.
    Reused by both webhook and legacy endpoint.
    """
    # Get or create WhatsApp session
    wa_session = (
        db.query(WhatsAppSession)
        .filter(WhatsAppSession.phone_number == phone_number)
        .first()
    )

    if not wa_session:
        wa_session = WhatsAppSession(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            session_id=str(uuid.uuid4()),
        )
        db.add(wa_session)
        db.commit()
        db.refresh(wa_session)

    session_id = wa_session.session_id

    # Update last message time
    wa_session.last_message_at = get_sl_time()
    db.commit()

    # Get conversation history
    history_messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at.asc())
        .all()
    )

    conversation_history = [
        {"role": msg.role, "content": msg.content} for msg in history_messages
    ]

    # Generate response
    rag_service = RAGService()
    result = rag_service.generate_response(
        query=message,
        conversation_history=conversation_history,
        phone_number=phone_number,
    )

    # Save user message
    user_msg = ConversationMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=message,
    )
    db.add(user_msg)

    # Save assistant response
    assistant_msg = ConversationMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=result["response"],
    )
    db.add(assistant_msg)
    db.commit()

    # Send response via WASender (Running in background task)
    background_tasks.add_task(
        send_wasender_message_background,
        phone_number=phone_number,
        message=result["response"],
        session_id=session_id
    )

    return {
        "response": result["response"],
        "phone_number": phone_number,
        "session_id": session_id,
        "category_image": result.get("category_image"),
        "status": "processed"
    }


@router.post("/message")
async def handle_whatsapp_message(
    request: WhatsAppMessage, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Legacy endpoint for internal testing or old node service.
    Now forwards to the unified processing logic.
    """
    return await process_message_internal(
        request.phone_number, 
        request.message, 
        db, 
        background_tasks
    )


@router.get("/sessions")
async def list_whatsapp_sessions(db: Session = Depends(get_db)):
    """List all WhatsApp sessions."""
    sessions = (
        db.query(WhatsAppSession).order_by(WhatsAppSession.last_message_at.desc()).all()
    )

    return {
        "sessions": [
            {
                "id": s.id,
                "phone_number": s.phone_number,
                "session_id": s.session_id,
                "created_at": s.created_at,
                "last_message_at": s.last_message_at,
            }
            for s in sessions
        ]
    }


@router.delete("/sessions/{phone_number}")
async def clear_whatsapp_session(phone_number: str, db: Session = Depends(get_db)):
    """Clear WhatsApp session and history."""
    wa_session = (
        db.query(WhatsAppSession)
        .filter(WhatsAppSession.phone_number == phone_number)
        .first()
    )

    if wa_session:
        # Clear conversation history
        db.query(ConversationMessage).filter(
            ConversationMessage.session_id == wa_session.session_id
        ).delete()

        # Delete session
        db.delete(wa_session)
        db.commit()

    return {"message": "Session cleared", "phone_number": phone_number}
