#!/usr/bin/env python3
"""
Test API key sau khi restart - simulate như uvicorn load
"""
import anthropic
import os
from dotenv import load_dotenv

# Load exactly như src.main load
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

print("=" * 70)
print("TEST API KEY (After Restart Simulation)")
print("=" * 70)
print(f"API Key: {api_key[:30]}...{api_key[-15:]}")
print(f"Length: {len(api_key)} chars")
print(f"Model: {model}")

try:
    client = anthropic.Anthropic(api_key=api_key)
    
    print(f"\n🧪 Testing with Anthropic API...")
    message = client.messages.create(
        model=model,
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Reply with just 'OK'"}
        ]
    )
    
    print(f"✅ SUCCESS! API key works")
    print(f"Response: {message.content[0].text}")
    
except anthropic.NotFoundError as e:
    print(f"\n❌ MODEL NOT FOUND (404 Error)")
    print(f"Error: {e}")
    print(f"\n💡 This API key CANNOT access model: {model}")
    print(f"   Key prefix: {api_key[:20]}...")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Details: {e}")
