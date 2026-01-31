from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse
from typing import Optional
import uuid

from ..config import get_settings
from .embedding_service import EmbeddingService


class VectorStoreService:
    """Service for managing vectors in Qdrant."""

    def __init__(self):
        settings = get_settings()
        # Log connection attempt with masked key
        masked_key = (
            f"{settings.qdrant_api_key[:5]}...{settings.qdrant_api_key[-5:]}"
            if settings.qdrant_api_key
            else "None"
        )
        print(f"Connecting to Qdrant at: {settings.qdrant_url}")
        print(f"Collection: {settings.qdrant_collection_name}")
        print(f"API Key: {masked_key}")

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=60.0,
        )
        self.collection_name = settings.qdrant_collection_name
        self.embedding_service = EmbeddingService()
        self._ensure_collection()
        print("Successfully connected to vector database")

    def _ensure_collection(self):
        """Create collection if it doesn't exist (idempotent)."""
        try:
            # Check if collection exists
            if not self.client.collection_exists(self.collection_name):
                print(f"Collection '{self.collection_name}' not found. Creating...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.embedding_service.get_embedding_dimension(),
                        distance=qdrant_models.Distance.COSINE,
                    ),
                )
                print(f"Collection '{self.collection_name}' created successfully")
        except UnexpectedResponse as e:
            # Handle 403 Forbidden specifically
            if e.status_code == 403:
                print(
                    "\n\033[91mERROR: Qdrant 403 Forbidden.\033[0m\n"
                    "This usually means your API Key is invalid or not allowed to access/create this collection.\n"
                    f"configured collection: '{self.collection_name}'\n"
                    "Please check your QDRANT_API_KEY and QDRANT_COLLECTION_NAME in .env\n"
                )
                raise
            
            # Handle race condition: collection created between check and create
            if "already exists" in str(e):
                pass  # Collection exists, safe to continue
            else:
                raise

    def add_products(
        self, products: list[dict], document_id: str
    ) -> list[str]:
        """Add products to vector store."""
        from .document_processor import DocumentProcessor

        processor = DocumentProcessor()
        points = []
        point_ids = []

        for product in products:
            # Create embedding text
            embedding_text = processor.create_embedding_text(product)

            # Generate embedding
            embedding = self.embedding_service.generate_embedding(embedding_text)

            # Create unique ID
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            # Create point with metadata
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "category": product.get("category", ""),
                        "sub_category": product.get("sub_category", ""),
                        "sub_sub_category": product.get("sub_sub_category", ""),
                        "product_name": product.get("product_name", ""),
                        "variant": product.get("variant", ""),
                        "size_weight": product.get("size_weight", ""),
                        # "price_lkr": product.get("price_lkr", 0),  <-- REMOVED
                        "description": product.get("description", ""),
                        # "available": product.get("available", "Yes"), <-- REMOVED
                        "tags": product.get("tags", ""),
                        "embedding_text": embedding_text,
                    },
                )
            )

        # Batch upload
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)

        return point_ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_category: Optional[str] = None,
        score_threshold: float = 0.45,
    ) -> list[dict]:
        """Search for similar products.

        Args:
            query: Search query text
            top_k: Maximum number of results to return
            filter_category: Optional category filter
            score_threshold: Minimum similarity score (0.0-1.0). Default 0.45.
                            Only results with score >= threshold are returned.
        """
        # Generate query embedding
        query_embedding = self.embedding_service.generate_query_embedding(query)

        # Build filter if category specified
        search_filter = None
        if filter_category:
            search_filter = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="category",
                        match=qdrant_models.MatchValue(value=filter_category),
                    )
                ]
            )

        # Search with score threshold
        # Search with score threshold
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            query_filter=search_filter,
            score_threshold=score_threshold,
        ).points

        # Format results (all results are now above threshold)
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "id": result.id,
                    "score": result.score,
                    "category": result.payload.get("category"),
                    "sub_category": result.payload.get("sub_category"),
                    "sub_sub_category": result.payload.get("sub_sub_category"),
                    "product_name": result.payload.get("product_name"),
                    "variant": result.payload.get("variant"),
                    "size_weight": result.payload.get("size_weight"),
                    "price_lkr": result.payload.get("price_lkr"),
                    "description": result.payload.get("description"),
                    "available": result.payload.get("available"),
                }
            )

        return formatted_results

    def delete_by_document_id(self, document_id: str) -> int:
        """Delete all vectors for a document."""
        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="document_id",
                            match=qdrant_models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )
        return result

    def get_collection_info(self) -> dict:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.value,
            }
        except Exception as e:
            return {"error": str(e)}

    def clear_collection(self):
        """Delete all vectors in collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            return True
        except Exception:
            return False
