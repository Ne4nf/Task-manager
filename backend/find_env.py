import os
from dotenv import load_dotenv, find_dotenv

# Find all .env files
print("=" * 70)
print("FINDING .ENV FILES")
print("=" * 70)

# Check current directory and parents
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Try to find .env
dotenv_path = find_dotenv()
print(f"\nfind_dotenv() found: {dotenv_path}")

# Check if .env exists in various locations
locations = [
    "d:\\code-memory UI\\backend\\.env",
    "d:\\code-memory UI\\.env",
    ".env",
    "../.env"
]

print("\nChecking .env existence:")
for loc in locations:
    exists = os.path.exists(loc)
    print(f"  {loc}: {'✓ EXISTS' if exists else '✗ NOT FOUND'}")
    if exists:
        with open(loc, 'r') as f:
            for line in f:
                if 'ANTHROPIC_API_KEY' in line:
                    print(f"    -> {line.strip()[:80]}...")

# Load and check what we get
print("\n" + "=" * 70)
load_dotenv()
key = os.getenv('ANTHROPIC_API_KEY')
if key:
    print(f"Loaded key: {key[:30]}...{key[-15:]} ({len(key)} chars)")
