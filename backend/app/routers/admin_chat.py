from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db, WhatsAppSession, ConversationMessage

router = APIRouter(prefix="/admin", tags=["Admin Chat"])

class CustomerResponse(BaseModel):
    phone: str
    message_count: int
    last_active: datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    role: str
    content: str
    time: datetime

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    phone: str
    messages: List[MessageResponse]

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(db: Session = Depends(get_db)):
    """List all customers (WhatsApp sessions)."""
    # Since we don't have a dedicated Users/Customers table for WhatsApp users yet,
    # we use WhatsAppSession as the source of truth for "Customers".
    
    sessions = db.query(WhatsAppSession).all()
    customers = []
    
    for session in sessions:
        # Count messages for this session
        msg_count = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.session_id
        ).count()
        
        customers.append({
            "phone": session.phone_number,
            "message_count": msg_count,
            "last_active": session.last_message_at or session.created_at
        })
        
    # Sort by last active desc
    customers.sort(key=lambda x: x["last_active"], reverse=True)
    
    return customers

@router.get("/chat-history/{phone}", response_model=ChatHistoryResponse)
async def get_chat_history(phone: str, db: Session = Depends(get_db)):
    """Get chat history for a specific phone number."""
    
    # Verify session exists
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Fetch messages
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session.session_id
    ).order_by(ConversationMessage.created_at.asc()).all()
    
    return {
        "phone": phone,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "time": msg.created_at
            } for msg in messages
        ]
    }
