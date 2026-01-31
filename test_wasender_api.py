#!/usr/bin/env python3
"""
Quick test script to verify WASender API key directly.
This bypasses Docker to test if your API key works.
"""

import requests
import os
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / ".env"
env_vars = {}

with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            value = value.strip().strip('"').strip("'")
            env_vars[key] = value

# Get configuration
api_url = env_vars.get('WASENDER_API_URL', 'https://www.wasenderapi.com/api/send-message')
bearer_token = env_vars.get('WASENDER_TOKEN')

print("=" * 70)
print("WASender API Test")
print("=" * 70)
print(f"API URL: {api_url}")
print(f"Token: {bearer_token[:6]}...{bearer_token[-4:]} (length: {len(bearer_token)})")
print()

if not bearer_token:
    print("❌ WASENDER_TOKEN not found in .env file!")
    exit(1)

# Test payload (won't actually send to avoid spamming)
test_payload = {
    "to": "+94760858499",
    "text": "🧪 Test message from verification script"
}

headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

print("Testing API connection...")
print("Payload:", test_payload)
print()

try:
    response = requests.post(
        api_url,
        json=test_payload,
        headers=headers,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS! Your WASender API key is valid!")
        print("The message was sent successfully.")
    elif response.status_code == 401:
        print("❌ AUTHENTICATION FAILED!")
        print()
        print("Your API key is invalid. Please:")
        print("  1. Go to your WASender dashboard")
        print("  2. Click the 🔑 icon to get the correct API key")
        print("  3. Update WASENDER_TOKEN in your .env file")
        print("  4. Make sure there are no extra spaces or quotes")
    else:
        print(f"⚠️  Unexpected response (HTTP {response.status_code})")
        print("Check the response above for details")
        
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR!")
    print("Cannot reach WASender API. Check your internet connection.")
except requests.exceptions.Timeout:
    print("❌ TIMEOUT!")
    print("Request took too long. Try again.")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("=" * 70)
