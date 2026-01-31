#!/usr/bin/env python3
"""
Direct test of WASender API to debug authentication issues.
"""

import requests

# Configuration - hardcoded for testing
api_url = "https://wasenderapi.com/api/send-message"
bearer_token = "1d368966fa8d5d8d797edde161840b51d14d6c00c58fdffd2002754aed2b8d61"

print("=" * 60)
print("WASender API Direct Test")
print("=" * 60)
print(f"URL: {api_url}")
print(f"URL (repr): {repr(api_url)}")
print(f"Token: {bearer_token[:6]}...{bearer_token[-4:]}")
print(f"Token length: {len(bearer_token)}")
print("=" * 60)

# Test payload
payload = {
    "to": "+1234567890",
    "text": "Test message from Python"
}

# Headers
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

print("\nRequest Details:")
print(f"Payload: {payload}")
print(f"Authorization header starts with: {headers['Authorization'][:30]}...")
print("=" * 60)

try:
    print("\nSending request...")
    response = requests.post(
        api_url,
        json=payload,
        headers=headers,
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✅ SUCCESS! Authentication working!")
    elif response.status_code == 401:
        print("\n❌ 401 Authentication Failed")
        print("The token itself may be invalid or the API might expect a different format")
    else:
        print(f"\n⚠️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
