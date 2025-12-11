import anthropic
import time
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")

print("⏳ Đợi 30 giây để key được activate...")
time.sleep(30)

print("\n🧪 Testing key sau khi đợi...")
try:
    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=20,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(f"✅ SUCCESS! Key đã hoạt động!")
    print(f"Response: {message.content[0].text}")
except anthropic.AuthenticationError as e:
    print(f"❌ Vẫn bị lỗi: {e}")
    print("\n🔍 Hãy kiểm tra:")
    print("1. Vào https://console.anthropic.com/settings/plans")
    print("2. Xem 'Credits remaining' > 0")
    print("3. Billing method đã setup chưa")
