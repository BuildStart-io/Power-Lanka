"""
Prompt Loader Service
Loads and formats prompts from YAML files for easy editing and maintenance.
"""

import yaml
from pathlib import Path
from typing import Optional
from functools import lru_cache

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent


@lru_cache(maxsize=None)
def _load_yaml(filename: str) -> dict:
    """Load a YAML file and cache it."""
    filepath = PROMPTS_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def reload_prompts():
    """Clear the cache to reload prompts from disk."""
    _load_yaml.cache_clear()


def get_categories() -> str:
    """Get all product categories."""
    data = _load_yaml("categories.yaml")
    return data.get("categories", "").strip()


def get_first_message_instruction(categories: Optional[str] = None) -> str:
    """Get first message instruction with categories injected."""
    data = _load_yaml("first_message.yaml")
    instruction = data.get("instruction", "")

    if categories is None:
        categories = get_categories()

    return instruction.format(categories=categories).strip()


def get_returning_customer_instruction() -> str:
    """Get returning customer instruction."""
    data = _load_yaml("returning_customer.yaml")
    return data.get("instruction", "").strip()


def get_off_topic_instruction() -> str:
    """Get off-topic/irrelevant query handling instruction."""
    data = _load_yaml("off_topic.yaml")
    return data.get("instruction", "").strip()


def get_system_prompt_parts() -> dict:
    """Get all parts of the system prompt."""
    data = _load_yaml("system_prompt.yaml")
    return {
        "role": data.get("role", "").strip(),
        "personality": data.get("personality", "").strip(),
        "language_rules": data.get("language_rules", "").strip(),
        "formatting": data.get("formatting", "").strip(),
        "product_accuracy": data.get("product_accuracy", "").strip(),
        "sales_techniques": data.get("sales_techniques", "").strip(),
        "common_scenarios": data.get("common_scenarios", "").strip(),
        "ordering_protocol": data.get("ordering_protocol", "").strip(),
        "business_policies": data.get("business_policies", "").strip(),
        "off_topic": get_off_topic_instruction(),
    }


def get_query_expand_prompt(query: str) -> str:
    """Get the query expansion prompt with query injected."""
    data = _load_yaml("query_expand.yaml")
    prompt = data.get("prompt", "")
    return prompt.format(query=query).strip()


def get_query_expand_fallback() -> str:
    """Get the fallback query for expansion failures."""
    data = _load_yaml("query_expand.yaml")
    return data.get("default_fallback", "popular hair extension products tools")


def get_query_rewrite_prompt(query: str, history: str) -> str:
    """Get the query rewrite prompt with query and history injected."""
    data = _load_yaml("query_rewrite.yaml")
    prompt = data.get("prompt", "")
    return prompt.format(query=query, history=history).strip()


def build_full_prompt(
    query: str,
    context: str,
    history: str,
    is_first_message: bool,
    categories: Optional[str] = None,
) -> str:
    """
    Build the complete prompt for the LLM.

    Args:
        query: Customer's message
        context: Retrieved product context
        history: Conversation history
        is_first_message: Whether this is the customer's first message
        categories: Optional categories string (uses default if not provided)

    Returns:
        Complete formatted prompt string
    """
    if categories is None:
        categories = get_categories()

    # Get system prompt parts
    parts = get_system_prompt_parts()

    # Get appropriate instruction based on conversation state
    if is_first_message:
        state_instruction = get_first_message_instruction(categories)
    else:
        state_instruction = get_returning_customer_instruction()

    # Build history section
    if history:
        history_section = f"## CONVERSATION HISTORY:\n{history}"
    else:
        history_section = "## CONVERSATION HISTORY:\n(This is the start of the conversation)"

    # Assemble the full prompt
    prompt = f"""{parts['role']}

{state_instruction}

{parts['personality']}

{parts['language_rules']}

{parts['formatting']}

{parts['product_accuracy']}

{parts['sales_techniques']}

{parts['ordering_protocol']}

{parts['business_policies']}

{parts['common_scenarios']}

{parts['off_topic']}

## PRODUCT CATALOG (Retrieved for this query):
{context}

## ALL AVAILABLE CATEGORIES:
{categories}

{history_section}

## CUSTOMER'S MESSAGE:
{query}

🚨 FINAL LANGUAGE CHECK - BEFORE YOU RESPOND:
- Output ONLY Sinhala (සිංහල Unicode) + English product names
- ❌ NO Chinese (告诉), Telugu (ప), Tamil (த), Hindi (ह) characters
- If you're about to write a character that looks different from Sinhala, DON'T!

## YOUR RESPONSE (natural, helpful, WhatsApp-formatted):
"""

    return prompt
