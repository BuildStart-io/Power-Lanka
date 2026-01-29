
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import uuid

from ..config import get_settings

settings = get_settings()

# Ensure data directory exists
os.makedirs(settings.data_dir, exist_ok=True)

DATABASE_URL = f"sqlite:///{settings.data_dir}/rag_agent.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Document(Base):
    """Uploaded documents table."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    product_count = Column(Integer, default=0)
    status = Column(String, default="processed")
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ConversationMessage(Base):
    """Conversation history table."""

    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WhatsAppSession(Base):
    """WhatsApp sessions table."""

    __tablename__ = "whatsapp_sessions"

    id = Column(String, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    session_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    """Product catalog table for dynamic data (price, availability)."""

    __tablename__ = "products"

    id = Column(String, primary_key=True)  # composite: name_variant
    product_name = Column(String, nullable=False, index=True)
    variant = Column(String, nullable=True)
    price_lkr = Column(Float, default=0.0)
    available = Column(String, default="Yes")
    image_paths = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """Orders table."""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Link to WhatsApp Session or Customer ID (using session ID for now)
    session_id = Column(String, ForeignKey("whatsapp_sessions.id"), nullable=False)
    
    # Status: 'pending' (cart), 'confirmed', 'completed', 'cancelled'
    status = Column(String, default="pending") 
    
    total_amount = Column(Float, default=0.0)
    payment_method = Column(String, nullable=True) # COD, Bank Transfer
    
    # Shipping Details
    shipping_name = Column(String, nullable=True)
    shipping_address = Column(String, nullable=True)
    shipping_district = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Line items for an order."""
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0) # Snapshot of price at time of order
    subtotal = Column(Float, default=0.0)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class User(Base):
    """Admin users table."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    role = Column(String, default="admin") # admin, staff
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Functions for DB Operations ---

def get_or_create_customer(db, phone: str):
    """Get or create a WhatsApp session (Customer)."""
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session:
        # In a real app we might want to create one, but usually message handler does this
        return None 
    return session

def get_pending_order(db, session_id: str):
    """Get the customer's active cart (pending order)."""
    return db.query(Order).filter(
        Order.session_id == session_id, 
        Order.status == 'pending'
    ).first()

def create_order(db, session_id: str):
    """Create a new pending order."""
    order = Order(session_id=session_id)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def add_order_item(db, order_id: str, product_id: str, quantity: int, price: float):
    """Add item to order or update quantity."""
    # Check if item exists
    item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id, 
        OrderItem.product_id == product_id
    ).first()
    
    if item:
        item.quantity += quantity
        item.subtotal = item.quantity * item.unit_price
    else:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=price,
            subtotal=quantity * price
        )
    db.add(item)
    
    db.commit()  # Commit item first
    
    # Update Order Total using db.get() (SQLAlchemy 2.x compatible)
    order = db.get(Order, order_id)
    if order:
        # Recalculate total from all items
        current_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        order.total_amount = sum(i.subtotal for i in current_items) + 350.0  # Fixed shipping
        db.commit()
    return item

def confirm_order_db(db, order_id: str, name: str, address: str, district: str, payment: str):
    """Update order status to confirmed."""
    order = db.get(Order, order_id)
    if order:
        order.shipping_name = name
        order.shipping_address = address
        order.shipping_district = district
        order.payment_method = payment
        order.status = "confirmed"
        db.commit()
        return order
    return None

def format_price(amount):
    return f"Rs. {amount:,.2f}"
