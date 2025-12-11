import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('ANTHROPIC_API_KEY')
model = os.getenv('CLAUDE_MODEL')

print("=" * 60)
print("ENVIRONMENT CHECK")
print("=" * 60)
print(f"API Key: {key[:30]}...{key[-15:]}")
print(f"Length: {len(key)} chars")
print(f"Model: {model}")
print(f"\nFirst 50 chars: {key[:50]}")
print(f"Last 50 chars: {key[-50:]}")
