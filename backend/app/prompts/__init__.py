"""Prompts package for RAG Agent."""

from .prompt_loader import (
    get_categories,
    get_first_message_instruction,
    get_returning_customer_instruction,
    get_off_topic_instruction,
    get_system_prompt_parts,
    get_query_expand_prompt,
    get_query_expand_fallback,
    get_query_rewrite_prompt,
    build_full_prompt,
    reload_prompts,
)

__all__ = [
    "get_categories",
    "get_first_message_instruction",
    "get_returning_customer_instruction",
    "get_off_topic_instruction",
    "get_system_prompt_parts",
    "get_query_expand_prompt",
    "get_query_expand_fallback",
    "get_query_rewrite_prompt",
    "build_full_prompt",
    "reload_prompts",
]
