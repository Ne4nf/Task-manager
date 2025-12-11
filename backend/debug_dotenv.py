from dotenv import find_dotenv, load_dotenv
import os

dotenv_path = find_dotenv()
print(f"Dotenv file found: {dotenv_path}")

load_dotenv()
key = os.getenv('ANTHROPIC_API_KEY')
print(f"\nLoaded key: {key[:30]}...{key[-15:]}")
print(f"Length: {len(key)}")

# Try loading explicitly
print(f"\n--- Loading from backend/.env explicitly ---")
load_dotenv('d:\\code-memory UI\\backend\\.env', override=True)
key2 = os.getenv('ANTHROPIC_API_KEY')
print(f"Key after explicit load: {key2[:30]}...{key2[-15:]}")
print(f"Length: {len(key2)}")
