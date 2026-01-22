from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..database import get_db, ConversationMessage, WhatsAppSession
from ..services import RAGService
from ..models import WhatsAppMessage

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/message")
async def handle_whatsapp_message(
    request: WhatsAppMessage, db: Session = Depends(get_db)
):
    """Handle incoming WhatsApp message - called by Node.js service."""
    # Get or create WhatsApp session
    wa_session = (
        db.query(WhatsAppSession)
        .filter(WhatsAppSession.phone_number == request.phone_number)
        .first()
    )

    if not wa_session:
        wa_session = WhatsAppSession(
            id=str(uuid.uuid4()),
            phone_number=request.phone_number,
            session_id=str(uuid.uuid4()),
        )
        db.add(wa_session)
        db.commit()
        db.refresh(wa_session)

    session_id = wa_session.session_id

    # Update last message time
    wa_session.last_message_at = datetime.utcnow()
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
        query=request.message,
        conversation_history=conversation_history,
    )

    # Save user message
    user_msg = ConversationMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=request.message,
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

    return {
        "response": result["response"],
        "phone_number": request.phone_number,
        "session_id": session_id,
        "category_image": result.get("category_image"),
    }


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
