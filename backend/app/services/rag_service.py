import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from typing import Optional
import logging
import re
from collections import Counter

from ..config import get_settings
from .vector_store import VectorStoreService
from .category_images import get_category_image
from ..prompts import (
    get_categories,
    get_query_expand_prompt,
    get_query_expand_fallback,
    get_query_rewrite_prompt,
    get_query_rewrite_prompt,
    build_full_prompt,
)
from ..agent.tools import add_to_cart, view_cart, save_shipping_details, confirm_order
import ast

logger = logging.getLogger(__name__)


class RAGService:
    """RAG pipeline service - retrieval and generation with human-like responses."""

    def __init__(self):
        self.settings = get_settings()
        
        # Configure Gemini
        if not self.settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set")
        else:
            genai.configure(api_key=self.settings.gemini_api_key)
            
        # Use Gemini Model
        self.model_name = self.settings.gemini_model
        self.model = genai.GenerativeModel(self.model_name)
        
        self.vector_store = VectorStoreService()
        self.top_k = self.settings.top_k_results
        self.categories = get_categories()

    def _get_conversation_state(self, conversation_history: Optional[list[dict]]) -> dict:
        """Detect conversation state for dynamic prompting."""
        if not conversation_history or len(conversation_history) == 0:
            return {
                "is_first_message": True,
                "message_count": 0,
            }

        # Count user messages only
        user_messages = [m for m in conversation_history if m.get("role") == "user"]
        message_count = len(user_messages)

        return {
            "is_first_message": False,
            "message_count": message_count,
        }

    def _generate_with_fallback(self, prompt: str):
        """Generate content using Gemini."""
        try:
            # Gemini generation
            response = self.model.generate_content(prompt)
            
            # Wrap response to match interface expected by caller
            class ResponseWrapper:
                def __init__(self, content):
                    self.text = content
            
            return ResponseWrapper(response.text)

        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            # Raise or return fallback? Raising allows retry/handling upstream
            raise e

    def _validate_script_purity(self, text: str) -> tuple[bool, str]:
        """Check if response contains only Sinhala + English characters.

        Detects contamination from Chinese, Telugu, Tamil, Hindi, and other scripts.
        Returns (is_valid, contaminated_script_name).
        """
        # Forbidden script patterns (Unicode ranges)
        patterns = {
            'Chinese': r'[\u4e00-\u9fff\u3400-\u4dbf]',  # CJK Unified Ideographs
            'Telugu': r'[\u0c00-\u0c7f]',                 # Telugu
            'Tamil': r'[\u0b80-\u0bff]',                  # Tamil
            'Hindi': r'[\u0900-\u097f]',                  # Devanagari
            'Bengali': r'[\u0980-\u09ff]',                # Bengali
            'Kannada': r'[\u0c80-\u0cff]',                # Kannada
            'Gujarati': r'[\u0a80-\u0aff]',               # Gujarati
            'Thai': r'[\u0e00-\u0e7f]',                   # Thai
            'Arabic': r'[\u0600-\u06ff]',                 # Arabic
            'Japanese': r'[\u3040-\u309f\u30a0-\u30ff]',  # Hiragana + Katakana
            'Korean': r'[\uac00-\ud7af]',                 # Hangul
        }

        for script_name, pattern in patterns.items():
            if re.search(pattern, text):
                return False, script_name

        return True, None

    def _strip_foreign_scripts(self, text: str) -> str:
        """Remove non-Sinhala/English characters as fallback cleanup.

        Keeps: Sinhala (0D80-0DFF), Basic Latin (0020-007F),
               General punctuation, and common emojis.
        """
        # Pattern to match characters we want to REMOVE
        # This keeps: Sinhala, Basic Latin, General Punctuation, Symbols, Emojis
        forbidden_ranges = (
            r'[\u0900-\u097f]'   # Hindi/Devanagari
            r'|[\u0980-\u09ff]'  # Bengali
            r'|[\u0a00-\u0a7f]'  # Gurmukhi
            r'|[\u0a80-\u0aff]'  # Gujarati
            r'|[\u0b00-\u0b7f]'  # Oriya
            r'|[\u0b80-\u0bff]'  # Tamil
            r'|[\u0c00-\u0c7f]'  # Telugu
            r'|[\u0c80-\u0cff]'  # Kannada
            r'|[\u0d00-\u0d7f]'  # Malayalam (close to Sinhala but distinct)
            r'|[\u0e00-\u0e7f]'  # Thai
            r'|[\u0600-\u06ff]'  # Arabic
            r'|[\u4e00-\u9fff]'  # Chinese CJK
            r'|[\u3400-\u4dbf]'  # Chinese CJK Extension A
            r'|[\u3040-\u309f]'  # Japanese Hiragana
            r'|[\u30a0-\u30ff]'  # Japanese Katakana
            r'|[\uac00-\ud7af]'  # Korean Hangul
        )
        return re.sub(forbidden_ranges, '', text)

    def _expand_first_message_query(self, query: str) -> str:
        """Expand first message query for better product retrieval."""
        expand_prompt = get_query_expand_prompt(query)

        try:
            response = self._generate_with_fallback(expand_prompt)
            expanded = response.text.strip()
            if len(expanded) > 100 or not expanded:
                return get_query_expand_fallback()
            logger.info(f"First message query expanded: {query} -> {expanded}")
            return expanded
        except Exception:
            return get_query_expand_fallback()

    def _rewrite_query(
        self, query: str, conversation_history: Optional[list[dict]] = None
    ) -> str:
        """Rewrite user query for better retrieval using conversation context."""
        if not conversation_history or len(conversation_history) < 2:
            return query

        # Build recent history context (last 4 messages)
        recent_history = conversation_history[-4:]
        history_text = "\n".join(
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in recent_history
        )

        rewrite_prompt = get_query_rewrite_prompt(query, history_text)

        try:
            response = self._generate_with_fallback(rewrite_prompt)
            rewritten = response.text.strip()
            # Fallback if response is too long or empty
            if len(rewritten) > 100 or not rewritten:
                return query
            return rewritten
        except Exception:
            return query

    def generate_response(
        self,
        query: str,
        conversation_history: Optional[list[dict]] = None,
        phone_number: str = None,
    ) -> dict:
        """Generate response using RAG pipeline with human-like sales agent behavior."""
        logger.info(f"RAG query: {query}")

        # Step 1: Get conversation state
        conv_state = self._get_conversation_state(conversation_history)
        is_first = conv_state["is_first_message"]
        logger.info(f"Conversation state: first_msg={is_first}, count={conv_state['message_count']}")

        # Step 2: Prepare search query
        if is_first:
            # For first message, expand query to get relevant products
            search_query = self._expand_first_message_query(query)
        else:
            # For subsequent messages, use context-aware rewriting
            search_query = self._rewrite_query(query, conversation_history)
            if search_query != query:
                logger.info(f"Query rewritten: {search_query}")

        # Step 3: Vector search
        search_results = self.vector_store.search(search_query, top_k=self.top_k)
        logger.info(f"Retrieved {len(search_results)} products (threshold filtered)")

        # Step 4: Category image logic (skip for first message to avoid random images)
        category_image = None
        if not is_first:
            IMAGE_SCORE_THRESHOLD = 0.50
            image_eligible_results = [
                r for r in search_results if r.get("score", 0) >= IMAGE_SCORE_THRESHOLD
            ]

            category_counts = Counter()
            sub_category_counts = Counter()

            for result in image_eligible_results:
                if result.get("category"):
                    category_counts[result["category"]] += 1
                if result.get("sub_category"):
                    sub_category_counts[result["sub_category"]] += 1

            categories = [c[0] for c in category_counts.most_common()]
            sub_categories = [c[0] for c in sub_category_counts.most_common()]

            category_image = get_category_image(categories, sub_categories)
            if category_image:
                logger.info(f"Category image found: {category_image}")

        # Step 5: Build context from results
        context = self._build_context(search_results)

        # Step 6: Build conversation history
        history_text = ""
        if conversation_history:
            history_text = self._build_history(conversation_history)

        # Step 7: Create dynamic prompt using YAML templates
        prompt = build_full_prompt(
            query=query,
            context=context,
            history=history_text,
            is_first_message=is_first,
            categories=self.categories,
        )

        # Step 8: Generate response with graceful error handling
        try:
            response = self._generate_with_fallback(prompt)
            response_text = response.text
            logger.info(f"Raw LLM Response: {response_text}")

            # Step 9: Validate script purity (detect Chinese, Telugu, etc.)
            is_valid, contaminated_script = self._validate_script_purity(response_text)
            if not is_valid:
                logger.warning(f"Script contamination detected: {contaminated_script} characters in response")
                # Strip foreign scripts as cleanup
                response_text = self._strip_foreign_scripts(response_text)
                response_text = self._strip_foreign_scripts(response_text)
                logger.info("Foreign script characters stripped from response")

            # Step 10: Process Tool Calls (Regex based)
            if phone_number:
                response_text = self._execute_tool_calls(response_text, phone_number)
                
        except (ResourceExhausted, Exception) as e:
            logger.error(f"API exhausted or failed during response generation: {str(e)}")
            response_text = (
                "⚠️ *System Busy*\n\n"
                "I apologize, but our AI service is currently experiencing high traffic. "
                "Please try asking your question again in 1-2 minutes. 🙏"
            )

        return {
            "response": response_text,
            "sources": search_results,
            "query": query,
            "category_image": category_image,
        }

    def _build_context(self, results: list[dict]) -> str:
        """Build context string from search results with live DB lookup."""
        if not results:
            return "No specific products matched. Show general catalog information."

        # Import here to avoid circular dependencies
        from ..database.database import SessionLocal, Product

        db = SessionLocal()
        context_parts = []
        
        try:
            for i, result in enumerate(results, 1):
                p_name = result.get('product_name', "").strip()
                p_variant = (result.get('variant') or "").strip()
                
                # Default "static" values (fallback)
                price = result.get('price_lkr', 0)
                available = result.get('available', 'Unknown')

                # Attempt Live Lookup
                if p_name:
                    p_id = f"{p_name}_{p_variant}" if p_variant else p_name
                    db_product = db.query(Product).filter(Product.id == p_id).first()
                    
                    if db_product:
                        price = db_product.price_lkr
                        available = db_product.available
                        # logger.info(f"Live Price Found for {p_id}: {price}")

                parts = [f"{i}. {p_name}"]

                if result.get("category"):
                    parts.append(f"   Category: {result['category']}")
                if result.get("sub_category"):
                    parts.append(f"   Sub-category: {result['sub_category']}")
                if result.get("sub_sub_category"):
                    parts.append(f"   Type: {result['sub_sub_category']}")
                if p_variant:
                    parts.append(f"   Variant: {p_variant}")
                if result.get("size_weight"):
                    parts.append(f"   Size/Weight: {result['size_weight']}")
                
                # Use the LIVE variables
                parts.append(f"   Price: RS.{price}")
                parts.append(f"   Available: {available}")
                    
                if result.get("description"):
                    parts.append(f"   Description: {result['description']}")

                context_parts.append("\n".join(parts))
        finally:
            db.close()

        return "\n\n".join(context_parts)

    def _build_history(self, history: list[dict]) -> str:
        """Build conversation history string."""
        history_parts = []
        for msg in history[-10:]:  # Last 10 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_parts.append(f"{role.capitalize()}: {content}")

        return "\n".join(history_parts)

    def _execute_tool_calls(self, text: str, phone: str) -> str:
        """Detect and execute tool calls in the response text."""
        # Pattern to match: function_name(arg1, arg2...)
        # We look for specific known tool names
        tools = {
            "add_to_cart": add_to_cart,
            "view_cart": view_cart,
            "save_shipping_details": save_shipping_details,
            "confirm_order": confirm_order
        }
        
        # This regex is a bit naive but works for standard calls. 
        # It captures the function name and the arguments string inside parentheses.
        # Updated regex to be more robust:
        # 1. Matches optional code block markers (```python etc)
        # 2. Matches tool name
        # 3. Matches parentheses and content across newlines
        pattern = r"(add_to_cart|view_cart|save_shipping_details|confirm_order)\s*\(([\s\S]*?)\)"
        
        matches = list(re.finditer(pattern, text))
        
        logger.info(f"Scanning response for tools. Text length: {len(text)}. Matches found: {len(matches)}")
        if not matches and "confirm_order" in text:
             logger.warning(f"Potential missed tool call in text: {text[:100]}...")
        
        # Execute distinct calls (avoid duplicates if repeated?)
        executed_results = []
        
        for match in matches:
            func_name = match.group(1)
            args_str = match.group(2)
            
            try:
                # Prepare arguments
                # We need to prepend 'phone' if it's not explicitly in the call, 
                # OR we inspect the args.
                # The Prompt says `add_to_cart(phone, ...)` so LLM might include it or not.
                # Let's try to parse args_str as a tuple
                
                # Wrap in tuple to parse: (args_str)
                # If args_str is empty, plain eval might fail, but tools take args.
                
                # Safe eval using ast.literal_eval is hard because users might put strings without quotes?
                # LLM is instructed to write code.
                
                # Trick: use eval() but with restricted globals/locals
                # We can inject 'phone' variable into the context
                
                local_scope = {"phone": phone}
                
                # If the string is distinct arguments `phone, "Items", 1`, wrapping in `func(...)` and evaling works.
                # We construct the full call string
                call_str = f"{func_name}({args_str})"
                
                # For safety, we only allow literal values + the 'phone' variable. 
                # But `add_to_cart` string might be complex.
                # Let's rely on our specific tools map.
                
                # Define a context where tools are available and 'phone' is a variable
                context = tools.copy()
                context['phone'] = phone
                
                # Execute
                result = eval(call_str, {"__builtins__": {}}, context)
                
                executed_results.append(f"\n\n⚙️ *System Action*: {result}")
                
            except Exception as e:
                logger.error(f"Tool execution failed for {func_name}: {e}")
                executed_results.append(f"\n\n❌ Action Failed: {str(e)}")
        
        # If we executed tools, append results to response
        # Also, maybe strip the tool call string from the user-facing response?
        # The user might find `add_to_cart(...)` confusing if left in text.
        
        final_text = text
        for match in matches:
            # Remove the call string from the final text to make it clean
            final_text = final_text.replace(match.group(0), "").strip()
            
        if executed_results:
            final_text += "".join(executed_results)
            
        return final_text

    def get_simple_response(self, query: str) -> str:
        """Get a simple response without sources (for WhatsApp)."""
        result = self.generate_response(query)
        return result["response"]
