import logging
import time
from typing import List
# import google.generativeai as genai
from ..config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using OpenRouter or Gemini."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = "openrouter"
        
        # Determine provider based on available keys
        if self.settings.openrouter_api_key:
            self.provider = "openrouter"
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.settings.openrouter_api_key,
            )
            self.model_name = "text-embedding-3-small"
            self.dimension = 1536
        else:
            logger.warning("No API key found for embeddings (OpenRouter).")
            self.provider = "none"
            self.dimension = 1536

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if self.provider == "openrouter":
            return self._generate_openai_embedding(text)
        return [0.0] * self.dimension

    def _generate_openai_embedding(self, text: str) -> List[float]:
        try:
            # Simple retry logic
            for _ in range(3):
                try:
                    clean_text = text.replace("\n", " ")
                    response = self.client.embeddings.create(
                        input=clean_text,
                        model=self.model_name
                    )
                    return response.data[0].embedding
                except Exception as e:
                    logger.warning(f"OpenRouter embedding failed, retrying: {e}")
                    time.sleep(1)
            
            response = self.client.embeddings.create(
                input=text.replace("\n", " "),
                model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate OpenRouter embedding: {str(e)}")
            return [0.0] * self.dimension

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        return self.generate_embedding(query)

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        batch_size = 50
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                clean_batch = [t.replace("\n", " ") for t in batch]
                response = self.client.embeddings.create(
                    input=clean_batch,
                    model=self.model_name
                )
                data = sorted(response.data, key=lambda x: x.index)
                embeddings.extend([d.embedding for d in data])
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                for text in batch:
                    embeddings.append(self.generate_embedding(text))
                    
        return embeddings

    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings."""
        return self.dimension
