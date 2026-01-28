#!/usr/bin/env python3
import sys
import os
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_path)
from app.services.vector_store import VectorStoreService

def check_client():
    store = VectorStoreService()
    print("Client type:", type(store.client))
    print("Has search?", hasattr(store.client, 'search'))
    print("Has query_points?", hasattr(store.client, 'query_points'))

if __name__ == "__main__":
    check_client()
