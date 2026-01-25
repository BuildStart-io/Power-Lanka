import logging
import time
from typing import List
from ..config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using OpenRouter (OpenAI Compatible)."""

    def __init__(self):
        self.settings = get_settings()
        from openai import OpenAI
        
        # Use OpenRouter for embeddings too
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key,
        )
        self.model_name = "text-embedding-3-small"

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI."""
        try:
            # Simple retry logic
            for _ in range(3):
                try:
                    # Clean text slightly (remove newlines usually helps)
                    clean_text = text.replace("\n", " ")
                    response = self.client.embeddings.create(
                        input=clean_text,
                        model=self.model_name
                    )
                    return response.data[0].embedding
                except Exception as e:
                    logger.warning(f"Embedding failed, retrying: {e}")
                    time.sleep(1)
            
            # Final attempt
            response = self.client.embeddings.create(
                input=text.replace("\n", " "),
                model=self.model_name
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            # Return zero vector of correct dimension (1536)
            return [0.0] * 1536

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        return self.generate_embedding(query)

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        batch_size = 50  # Conservative batching
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                # OpenAI supports batting
                clean_batch = [t.replace("\n", " ") for t in batch]
                response = self.client.embeddings.create(
                    input=clean_batch,
                    model=self.model_name
                )
                # Sort by index to be safe, though usually preserves order
                data = sorted(response.data, key=lambda x: x.index)
                embeddings.extend([d.embedding for d in data])
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                # Fallback to individual
                for text in batch:
                    embeddings.append(self.generate_embedding(text))
                    
        return embeddings

    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings."""
        return 1536
