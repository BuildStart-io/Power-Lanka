#!/usr/bin/env python3
"""
Quick script to verify environment variables are properly configured.
Run this to check if WASender API token is correctly loaded.
"""

import os
from pathlib import Path

# Load .env file manually
env_file = Path(__file__).parent / ".env"

print("=" * 60)
print("Environment Variable Verification")
print("=" * 60)

if not env_file.exists():
    print("❌ .env file not found!")
    exit(1)

print(f"✅ .env file found at: {env_file}")
print()

# Parse .env file
env_vars = {}
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            # Remove quotes if present
            value = value.strip().strip('"').strip("'")
            env_vars[key] = value

# Check critical variables
critical_vars = [
    'WASENDER_TOKEN',
    'WASENDER_API_URL',
    'WHATSAPP_WEBHOOK_SIGNATURE',
    'OPENROUTER_API_KEY',
    'QDRANT_URL',
    'QDRANT_API_KEY'
]

print("Critical Environment Variables:")
print("-" * 60)

for var in critical_vars:
    if var in env_vars:
        value = env_vars[var]
        # Mask sensitive values
        if 'TOKEN' in var or 'KEY' in var:
            if len(value) > 10:
                display_value = f"{value[:6]}...{value[-4:]} (length: {len(value)})"
            else:
                display_value = "*** (too short!)"
        else:
            display_value = value
        
        # Check for common issues
        issues = []
        if value.startswith(' ') or value.endswith(' '):
            issues.append("⚠️  Has leading/trailing spaces!")
        if '\n' in value or '\r' in value:
            issues.append("⚠️  Contains newline characters!")
        if len(value) == 0:
            issues.append("⚠️  Empty value!")
        
        status = "✅" if not issues else "⚠️ "
        print(f"{status} {var}: {display_value}")
        for issue in issues:
            print(f"     {issue}")
    else:
        print(f"❌ {var}: NOT SET")

print()
print("=" * 60)
print("WASender Configuration Check:")
print("-" * 60)

wasender_token = env_vars.get('WASENDER_TOKEN', '')
if wasender_token:
    print(f"✅ WASENDER_TOKEN is set (length: {len(wasender_token)})")
    print(f"   First 6 chars: {wasender_token[:6]}")
    print(f"   Last 4 chars: {wasender_token[-4:]}")
    
    # Check if it looks valid (WASender tokens are usually 64 chars hex)
    if len(wasender_token) == 64:
        print("   ✅ Length looks correct (64 characters)")
    else:
        print(f"   ⚠️  Unexpected length (expected 64, got {len(wasender_token)})")
    
    # Check if it's all hex
    try:
        int(wasender_token, 16)
        print("   ✅ Format looks valid (hexadecimal)")
    except ValueError:
        print("   ⚠️  Format might be invalid (not pure hexadecimal)")
else:
    print("❌ WASENDER_TOKEN is NOT set!")

print()
print("=" * 60)
print("\n🔧 Docker Compose Mapping:")
print("-" * 60)
print("In docker-compose.yml, the following mapping is used:")
print("  WASENDER_TOKEN (from .env) → WHATSAPP_API_BEARER_TOKEN (in container)")
print()
print("Make sure:")
print("  1. ✓ WASENDER_TOKEN is set in .env")
print("  2. ✓ docker-compose.yml has: WHATSAPP_API_BEARER_TOKEN=${WASENDER_TOKEN}")
print("  3. ✓ Run 'docker compose down && docker compose up -d' after changes")
print("=" * 60)
