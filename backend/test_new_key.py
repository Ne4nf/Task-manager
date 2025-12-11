import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

print("=" * 60)
print("TESTING NEW API KEY")
print("=" * 60)
print(f"Key: {api_key[:30]}...{api_key[-20:]}")
print(f"Length: {len(api_key)} chars")
print()

try:
    client = anthropic.Anthropic(api_key=api_key)
    
    # Test với model đơn giản nhất
    print("Testing with claude-3-haiku-20240307...")
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=20,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(f"✅ SUCCESS! Key is valid")
    print(f"Response: {message.content[0].text}")
    
except anthropic.AuthenticationError as e:
    print(f"❌ AUTHENTICATION ERROR")
    print(f"Error: {e}")
    print()
    print("⚠️ Possible issues:")
    print("1. API key not activated yet (wait 1-2 minutes)")
    print("2. Anthropic account has no credits")
    print("3. Key was copied incorrectly")
    print("4. Account billing issue")
    print()
    print("🔗 Check your account:")
    print("   https://console.anthropic.com/settings/keys")
    print("   https://console.anthropic.com/settings/plans")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
