from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Product Models
class Product(BaseModel):
    category: str
    sub_category: str
    sub_sub_category: Optional[str] = ""
    product_name: str
    variant: Optional[str] = ""
    size_weight: Optional[str] = ""
    price_lkr: float
    description: Optional[str] = ""
    available: Optional[str] = "Yes"
    tags: Optional[str] = ""


class ProductInDB(Product):
    id: str
    document_id: str
    created_at: datetime


# Document Models
class DocumentUpload(BaseModel):
    filename: str
    file_type: str
    product_count: int
    status: str


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    product_count: int
    uploaded_at: datetime
    status: str


# Chat Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: list[dict]
    session_id: str
    category_image: Optional[str] = None


# WhatsApp Models
class WhatsAppMessage(BaseModel):
    phone_number: str
    message: str
    session_id: Optional[str] = None
