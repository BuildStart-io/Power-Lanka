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
        
        # Debug logging for configuration
        logger.info("[WASender] Initializing WASender service")
        logger.info(f"[WASender] API URL: {self.api_url}")
        logger.info(f"[WASender] Device ID: {self.device_id or 'Not set'}")
        logger.info(f"[WASender] Timeout: {self.timeout}s")
        
        if self.bearer_token:
            # Mask the token for security - show first 6 and last 4 chars
            masked_token = f"{self.bearer_token[:6]}...{self.bearer_token[-4:]}" if len(self.bearer_token) > 10 else "***"
            logger.info(f"[WASender] Bearer Token: {masked_token} (length: {len(self.bearer_token)})")
        else:
            logger.error(
                "[WASender] ❌ WHATSAPP_API_BEARER_TOKEN not set - WASender messages will fail!"
            )
            logger.error(
                "[WASender] Please ensure WHATSAPP_API_BEARER_TOKEN is set in your environment"
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
    
    def _get_headers(self, api_token: Optional[str] = None) -> dict:
        """Build request headers with bearer token authentication."""
        headers = {"Content-Type": "application/json"}
        token = api_token or self.bearer_token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def send_message(self, phone_number: str, message: str, api_token: Optional[str] = None) -> bool:
        """
        Send a WhatsApp message via WASenderAPI.
        
        Args:
            phone_number: Recipient phone number (with or without country code)
            message: Text message to send
            api_token: Optional Bearer token to use for this request
            
        Returns:
            True if message sent successfully, False otherwise
        """
        token = api_token or self.bearer_token
        if not token:
            logger.error(
                "[WASender] Cannot send message - WHATSAPP_API_BEARER_TOKEN or api_token not set"
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
            
            # Mask token in headers for logging
            headers = self._get_headers(api_token)
            masked_headers = headers.copy()
            if 'Authorization' in masked_headers:
                auth_value = masked_headers['Authorization']
                if len(auth_value) > 20:
                    masked_headers['Authorization'] = f"{auth_value[:13]}...{auth_value[-4:]}"
            logger.debug(f"[WASender] Headers: {masked_headers}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(
                    f"[WASender] ✅ Message sent successfully (HTTP {response.status_code})"
                )
                return True
            elif response.status_code == 401:
                logger.error(
                    f"[WASender] ❌ Authentication failed (HTTP 401) - Invalid API key!"
                )
                logger.error(f"[WASender] Response: {response.text}")
                logger.error(
                    "[WASender] Please check:\n"
                    "  1. WHATSAPP_API_BEARER_TOKEN in .env file is correct\n"
                    "  2. No extra spaces/quotes around the token\n"
                    "  3. Token hasn't expired or been revoked\n"
                    "  4. You've restarted the Docker container after changing .env"
                )
                return False
            else:
                logger.warning(
                    f"[WASender] ⚠️ Unexpected status code: {response.status_code}"
                )
                logger.warning(f"[WASender] Response: {response.text}")
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
    session_id: Optional[str] = None,
    api_token: Optional[str] = None
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
    success = service.send_message(phone_number, message, api_token)
    
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
