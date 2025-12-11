#!/usr/bin/env python3
"""
Test Render deployment sau khi update API key
"""

import requests
import time

RENDER_URL = "https://task-manager-bzwfq.onrender.com"

print("=" * 60)
print("RENDER DEPLOYMENT TEST")
print("=" * 60)

# Test 1: Health check
print("\n1️⃣ Testing health endpoint...")
try:
    response = requests.get(f"{RENDER_URL}/health", timeout=10)
    if response.status_code == 200:
        print("✅ Health check: OK")
    else:
        print(f"⚠️ Health check: {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Config check
print("\n2️⃣ Testing config endpoint...")
try:
    response = requests.get(f"{RENDER_URL}/config-check", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print("✅ Config check: OK")
        print(f"   - API Key exists: {data.get('anthropic_key_exists')}")
        print(f"   - API Key length: {data.get('anthropic_key_length')} chars")
        print(f"   - Claude model: {data.get('claude_model')}")
        
        if data.get('anthropic_key_length') == 108:
            print("\n✅ API KEY ĐÃ ĐƯỢC CẬP NHẬT!")
        else:
            print("\n⚠️ API key length không đúng (cần 108 chars)")
    else:
        print(f"⚠️ Config check: {response.status_code}")
except Exception as e:
    print(f"❌ Config check failed: {e}")

print("\n" + "=" * 60)
print("HƯỚNG DẪN TEST TASK GENERATION")
print("=" * 60)
print("\n1. Vào frontend: https://task-manager-mijz.vercel.app")
print("2. Chọn 1 module bất kỳ")
print("3. Click 'Gen AI Tasks'")
print("4. Nếu thành công → ✅ Deployment hoàn tất!")
print("5. Nếu bị lỗi → Xem logs trên Render dashboard")
