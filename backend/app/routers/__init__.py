# Routers package
from .documents import router as documents_router
from .chat import router as chat_router
from .whatsapp import router as whatsapp_router
from .admin import router as admin_router
from .admin_products import router as admin_products_router
from .admin_chat import router as admin_chat_router

__all__ = [
    "documents_router",
    "chat_router",
    "whatsapp_router",
    "admin_router",
    "admin_products_router",
]
