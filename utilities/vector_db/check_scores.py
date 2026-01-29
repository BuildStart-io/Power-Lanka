#!/usr/bin/env python3
"""
Script to check similarity scores for different types of queries.
This helps determine the appropriate threshold for showing category images.
"""

import sys
import os

# Add the backend directory to the path
# Add the backend directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(project_root, 'backend'))

from app.services.vector_store import VectorStoreService


def test_query(vector_store: VectorStoreService, query: str, threshold: float = 0.0):
    """Test a single query and print results."""
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")

    # Search with no threshold to see all scores
    results = vector_store.search(query, top_k=5, score_threshold=threshold)

    if not results:
        print("No results found.")
        return

    print(f"\nTop {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   Category: {result['category']}")
        print(f"   Sub-category: {result['sub_category']}")
        print(f"   Product: {result['product_name']}")
        if result['variant']:
            print(f"   Variant: {result['variant']}")
        if result['size_weight']:
            print(f"   Size: {result['size_weight']}")
        print(f"   Price: RS.{result['price_lkr']}")
        print()


def main():
    print("\n" + "="*80)
    print("RAG AGENT - Similarity Score Analysis")
    print("="*80)

    # Initialize vector store
    print("\nInitializing VectorStoreService...")
    try:
        vector_store = VectorStoreService()
        print("✓ Connected to Qdrant")

        # Get collection info
        info = vector_store.get_collection_info()
        print(f"✓ Collection: {info['name']}")
        print(f"✓ Total products: {info['points_count']}")

    except Exception as e:
        print(f"✗ Error connecting to vector store: {e}")
        return

    # Test queries
    test_queries = [
        # Generic/greeting queries (should have low scores)
        "Hi",
        "Hello",
        "Hey there",
        "Good morning",

        # Generic product queries (should have medium scores)
        "What products do you have",
        "Show me your products",
        "What do you sell",

        # Specific product queries (should have high scores)
        "beads",
        "pliers",
        "hair extension",
        "Human Hair Bundles",
        "crimping tool",
        "blonde hair",
    ]

    print("\n" + "="*80)
    print("Testing queries with NO threshold (to see actual scores):")
    print("="*80)

    for query in test_queries:
        test_query(vector_store, query, threshold=0.0)

    # Summary with different thresholds
    print("\n" + "="*80)
    print("SUMMARY - Testing 'Hi' with different thresholds:")
    print("="*80)

    for threshold in [0.0, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60]:
        results = vector_store.search("Hi", top_k=5, score_threshold=threshold)
        print(f"\nThreshold {threshold:.2f}: {len(results)} results")
        if results:
            print(f"  Top score: {results[0]['score']:.4f}")
            print(f"  Lowest score: {results[-1]['score']:.4f}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("""
Based on the scores above, here are threshold recommendations:

1. If generic queries like "Hi" return scores < 0.50:
   - Use threshold 0.50 for category image display
   - Use threshold 0.45 for general product retrieval

2. If generic queries like "Hi" return scores < 0.55:
   - Use threshold 0.55 for category image display
   - Use threshold 0.50 for general product retrieval

3. If specific queries like "beads" return scores > 0.70:
   - Consider using a higher threshold (0.60-0.65) for category images
   - to ensure only relevant products trigger image display

The key is to find the gap between:
- Generic/greeting queries (should NOT trigger images)
- Vague product queries (might trigger images)
- Specific product queries (should definitely trigger images)
""")


if __name__ == "__main__":
    main()
