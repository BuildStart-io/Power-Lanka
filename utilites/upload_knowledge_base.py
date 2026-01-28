#!/usr/bin/env python3
"""
Script to upload full knowledge base from data.txt to Qdrant.
Parses sections, FAQs, and descriptions.
"""
import sys
import os
import uuid

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_path)

from app.services.vector_store import VectorStoreService
from app.services.embedding_service import EmbeddingService
from qdrant_client.http import models as qdrant_models

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data.txt")

def parse_data_file():
    """Read and parse data.txt into meaningful chunks."""
    if not os.path.exists(DATA_FILE_PATH):
        print(f"❌ File not found: {DATA_FILE_PATH}", flush=True)
        return []

    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = []
    
    # Split by double newlines to isolate paragraphs/QAs
    raw_blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
    
    current_product = "General Info"
    current_category = "General"
    
    for block in raw_blocks:
        lower_block = block.lower()
        
        # Context switching logic
        if "fly killer" in lower_block:
            current_product = "Power Fly Killer Spray"
            current_category = "Pest Control"
        elif "deepclean" in lower_block:
            current_product = "Power DeepClean"
            current_category = "Cleaning"
        elif "odour neutralizer" in lower_block:
            current_product = "Power Odour Neutralizer Spray"
            current_category = "Cleaning"
        elif "delivery" in lower_block or "ordering" in lower_block:
            current_product = "Delivery & Policy"
            current_category = "Policy"
            
        # Determine chunk type
        chunk_category = "Product Info"
        if "?" in block and ("Q:" in block or "Q" in block):
             chunk_category = "FAQ"
        
        # Clean up block
        clean_text = block.replace('\n', ' ').strip()
        
        # Create rich tags
        tags = [current_product, current_category, chunk_category]
        if "ingredients" in lower_block: tags.append("ingredients")
        if "safe" in lower_block: tags.append("safety")
        if "delivery" in lower_block: tags.append("delivery")
        tag_str = ", ".join(tags)

        chunks.append({
            "category": chunk_category,
            "sub_category": current_category,
            "product_name": current_product,
            "description": clean_text,
            "tags": tag_str,
        })
            
    print(f"📝 Parsed {len(chunks)} text chunks from data.txt", flush=True)
    return chunks

def upload_knowledge_base():
    print("=" * 50, flush=True)
    print("  Power Lanka - Upload Full Knowledge Base", flush=True)
    print("=" * 50, flush=True)
    
    chunks = parse_data_file()
    if not chunks:
        return
    
    try:
        vector_store = VectorStoreService()
        embedding_service = EmbeddingService()
        
        print(f"\n📡 Connected to Qdrant: {vector_store.collection_name}", flush=True)
        
        points = []
        for chunk in chunks:
            # Create embedding text - combine important fields
            embedding_text = f"{chunk['product_name']} {chunk['description']} {chunk['tags']}"
            
            # Generate embedding
            embedding = embedding_service.generate_embedding(embedding_text)
            
            point_id = str(uuid.uuid4())
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "document_id": "knowledge_base",
                        "category": chunk["category"],
                        "sub_category": chunk["sub_category"],
                        "product_name": chunk["product_name"],
                        "description": chunk["description"],
                        "tags": chunk["tags"],
                        "embedding_text": embedding_text,
                    },
                )
            )
        
        # Batch upload
        batch_size = 50
        print(f"🚀 Uploading {len(points)} chunks...", flush=True)
        
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            vector_store.client.upsert(
                collection_name=vector_store.collection_name,
                points=batch,
            )
        
        print(f"✅ Knowledge Base Uploaded Successfully!", flush=True)
        
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload_knowledge_base()
