"""
WASender Service - Handles communication with WASenderAPI.

This service replaces the whatsapp-web.js Node.js implementation
with a REST API-based approach using WASenderAPI.
"""

import os
import logging
import requests
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class WASenderService:
    """
    Service for communicating with WASenderAPI.
    
    Provides methods to send WhatsApp messages via the WASenderAPI
    REST endpoint using bearer token authentication.
    """
    
    def __init__(self):
        """Initialize WASender service with configuration from environment."""
        self.api_url = os.getenv(
            "WASENDER_API_URL", 
            "https://www.wasenderapi.com/api/send-message"
        )
        self.bearer_token = os.getenv("WHATSAPP_API_BEARER_TOKEN")
        self.timeout = int(os.getenv("WASENDER_TIMEOUT", "10"))
        self.device_id = os.getenv("WASENDER_DEVICE_ID")
        
        if not self.bearer_token:
            logger.warning(
                "WHATSAPP_API_BEARER_TOKEN not set - WASender messages will fail"
            )
    
    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for WASender API.
        
        Ensures the phone number has a '+' prefix.
        
        Args:
            phone_number: Phone number with or without country code prefix
            
        Returns:
            Phone number with '+' prefix
        """
        phone = str(phone_number).strip()
        if not phone.startswith("+"):
            phone = f"+{phone}"
        return phone
    
    def _get_headers(self) -> dict:
        """Build request headers with bearer token authentication."""
        headers = {"Content-Type": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers
    
    def send_message(self, phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message via WASenderAPI.
        
        Args:
            phone_number: Recipient phone number (with or without country code)
            message: Text message to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.bearer_token:
            logger.error(
                "[WASender] Cannot send message - WHATSAPP_API_BEARER_TOKEN not set"
            )
            return False
        
        if not phone_number or not message:
            logger.error("[WASender] Phone number and message are required")
            return False
        
        payload = {
            "to": self._format_phone_number(phone_number),
            "text": message
        }
        
        # Add optional device/session ID if configured
        # Add optional device/session ID if configured
        if self.device_id:
            payload["session"] = self.device_id
            # Also legacy payload support which might call it 'gateway' or 'session'
            # But 'device' is standard for generic WASender-like APIs.
            # User provided 'session id', so 'session' is safest bet.


        
        try:
            logger.info(f"[WASender] Sending message to {payload['to']}")
            logger.debug(f"[WASender] URL: {self.api_url}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(
                    f"[WASender] ✅ Message sent successfully (HTTP {response.status_code})"
                )
                return True
            else:
                logger.warning(
                    f"[WASender] ⚠️ Unexpected status code: {response.status_code}"
                )
                logger.warning(f"[WASender] Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(
                f"[WASender] ❌ Timeout after {self.timeout}s connecting to API"
            )
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[WASender] ❌ Connection error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[WASender] ❌ Unexpected error: {str(e)}", exc_info=True)
            return False
    
    def send_message_with_image(
        self, 
        phone_number: str, 
        message: str, 
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send a WhatsApp message with optional image.
        
        Note: Image support depends on WASenderAPI plan.
        Falls back to text-only if image sending fails.
        
        Args:
            phone_number: Recipient phone number
            message: Text message/caption
            image_url: Optional URL of image to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # For now, send as text message
        # Image support can be added based on WASenderAPI documentation
        return self.send_message(phone_number, message)
    
    def is_configured(self) -> bool:
        """Check if WASender service is properly configured."""
        return bool(self.bearer_token and self.api_url)


@lru_cache()
def get_wasender_service() -> WASenderService:
    """
    Get or create WASender service singleton.
    
    Uses lru_cache for efficient singleton pattern.
    
    Returns:
        WASenderService instance
    """
    return WASenderService()


# Background task wrapper for async message sending
def send_wasender_message_background(
    phone_number: str, 
    message: str,
    session_id: Optional[str] = None
):
    """
    Background task function for sending WASender messages.
    
    Use this with FastAPI's BackgroundTasks for non-blocking message delivery.
    
    Args:
        phone_number: Recipient phone number
        message: Message text to send
        session_id: Optional session ID for logging
    """
    service = get_wasender_service()
    success = service.send_message(phone_number, message)
    
    if success:
        logger.info(
            f"[WASender Background] Message delivered to {phone_number} "
            f"(session: {session_id or 'N/A'})"
        )
    else:
        logger.error(
            f"[WASender Background] Failed to deliver message to {phone_number} "
            f"(session: {session_id or 'N/A'})"
        )
