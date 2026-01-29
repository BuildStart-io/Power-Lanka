import sys
import os

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from qdrant_client import QdrantClient
from app.config import get_settings

def reset_collection():
    settings = get_settings()
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )
    collection_name = settings.qdrant_collection_name
    
    print(f"Deleting collection: {collection_name}...")
    try:
        client.delete_collection(collection_name)
        print("✅ Collection deleted.")
    except Exception as e:
        print(f"❌ Error (might not exist): {e}")

if __name__ == "__main__":
    reset_collection()
