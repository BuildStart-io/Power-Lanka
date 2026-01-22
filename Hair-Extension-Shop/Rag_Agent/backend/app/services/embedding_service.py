import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from typing import Union
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Gemini."""

    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = self.settings.gemini_embedding_model
        # Hardcoded backup key provided by user for emergency fallback
        self.backup_api_key = "AIzaSyAp6dq-VqjuTtmLeoTcYV5pSRLrnDMsUio"

    def _embed_with_fallback(self, content: str, task_type: str) -> dict:
        """Generate embedding with fallback to backup API key on 429 errors."""
        try:
            return genai.embed_content(
                model=f"models/{self.model}",
                content=content,
                task_type=task_type,
            )
        except ResourceExhausted:
            logger.warning("Primary API key exhausted (429) during embedding. Switching to backup key.")
            try:
                # Re-configure with backup key
                genai.configure(api_key=self.backup_api_key)
                # Retry embedding
                return genai.embed_content(
                    model=f"models/{self.model}",
                    content=content,
                    task_type=task_type,
                )
            except Exception as e:
                logger.error(f"Backup key failed during embedding: {str(e)}")
                # Revert to primary key configuration
                genai.configure(api_key=self.settings.gemini_api_key)
                raise e

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        result = self._embed_with_fallback(
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def generate_query_embedding(self, query: str) -> list[float]:
        """Generate embedding for a query (optimized for retrieval)."""
        result = self._embed_with_fallback(
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        # Process in batches to avoid rate limits
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            for text in batch:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings."""
        # text-embedding-004 produces 768-dimensional embeddings
        return 768
