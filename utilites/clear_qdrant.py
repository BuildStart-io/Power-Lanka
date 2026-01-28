#!/usr/bin/env python3
"""
Script to clear the Qdrant vector database.
"""
import sys
import os

# Add backend to path - go up one level from utilites, then into backend
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_path)

from app.services.vector_store import VectorStoreService

def clear_vector_db():
    print("=" * 50, flush=True)
    print("  Power Lanka - Clear Vector DB", flush=True)
    print("=" * 50, flush=True)
    
    try:
        store = VectorStoreService()
        print(f"📡 Connected to Qdrant: {store.collection_name}", flush=True)
        
        info = store.get_collection_info()
        print(f"📊 Before cleaning: {info.get('points_count', 'unknown')} points", flush=True)
        
        # Clear collection
        store.clear_collection()
        print("✅ Collection cleared successfully!", flush=True)
        
        info = store.get_collection_info()
        print(f"📊 After cleaning: {info.get('points_count', 'unknown')} points", flush=True)
        
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)

if __name__ == "__main__":
    clear_vector_db()
