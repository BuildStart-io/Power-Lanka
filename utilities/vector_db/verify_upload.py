#!/usr/bin/env python3
"""
Verify that specific specific details from data.txt are present in Qdrant.
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "../..", "backend")
sys.path.insert(0, backend_path)

from app.services.vector_store import VectorStoreService

def verify_upload():
    print("=" * 50)
    print("  Power Lanka - Knowledge Base Verification")
    print("=" * 50)
    
    store = VectorStoreService()
    
    # List of specific unique phrases to check
    test_phrases = [
        "Captain Ceylon Pvt Ltd",
        "ginger tea and manioc",
        "cinnamon and turmeric",
        "MS-DS Certificate issued by the ITI",
        "damaging the fly's nervous system",
        "Chelating Power",
        "Surfactant Strength",
        "rust rings in sinks",
        "Power Odour Neutralizer Spray"
    ]
    
    print(f"\n📡 Checking Qdrant Collection: {store.collection_name}\n")
    
    all_found = True
    
    for phrase in test_phrases:
        # Search for this exact phrase
        results = store.search(phrase, top_k=1, score_threshold=0.3)
        
        if results:
            match = results[0]
            # print(f"✅ FOUND: '{phrase}'")
            # print(f"   Context: {match['description'][:60]}...")
            print(f"✅ FOUND: '{phrase}'")
        else:
            print(f"❌ MISSING: '{phrase}'")
            all_found = False
            
    print("-" * 50)
    if all_found:
        print("🎉 SUCCESS: All key details are present in the Vector DB!")
    else:
        print("⚠️ WARNING: Some details might be missing.")

if __name__ == "__main__":
    verify_upload()
