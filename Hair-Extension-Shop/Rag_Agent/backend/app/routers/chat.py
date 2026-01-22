from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..database import get_db, ConversationMessage
from ..services import RAGService
from ..models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get RAG-powered response."""
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())

    # Get conversation history for this session
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

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        session_id=session_id,
        category_image=result.get("category_image"),
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get conversation history for a session."""
    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at.asc())
        .all()
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
            }
            for msg in messages
        ],
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Clear conversation history for a session."""
    db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).delete()
    db.commit()

    return {"message": "History cleared", "session_id": session_id}


@router.post("/simple")
async def simple_chat(request: ChatRequest):
    """Simple chat without history (for quick testing)."""
    rag_service = RAGService()
    result = rag_service.generate_response(query=request.message)

    return {
        "response": result["response"],
        "sources": result["sources"],
        "category_image": result.get("category_image"),
    }
