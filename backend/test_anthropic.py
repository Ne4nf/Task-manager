#!/usr/bin/env python3
"""
Test Anthropic API key validity and model availability
"""
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def test_anthropic():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("=" * 60)
    print("ANTHROPIC API TEST")
    print("=" * 60)
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return
    
    print(f"✓ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"  Length: {len(api_key)} chars")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Test with the model from config
        model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        print(f"\n🧪 Testing model: {model}")
        
        message = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'API test successful' in JSON format"}
            ]
        )
        
        print(f"✅ SUCCESS! Model works correctly")
        print(f"Response: {message.content[0].text[:100]}")
        
    except anthropic.NotFoundError as e:
        print(f"\n❌ MODEL NOT FOUND ERROR!")
        print(f"Error: {e}")
        print(f"\nℹ️  This means:")
        print(f"   1. Model name '{model}' doesn't exist")
        print(f"   2. Or API key doesn't have access to this model")
        print(f"\n💡 Try these models instead:")
        print(f"   - claude-3-5-sonnet-20241022")
        print(f"   - claude-3-5-sonnet-latest") 
        print(f"   - claude-3-opus-20240229")
        print(f"   - claude-3-sonnet-20240229")
        
    except anthropic.AuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR!")
        print(f"Error: {e}")
        print(f"API key is invalid or expired")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_anthropic()
