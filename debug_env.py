import os
from dotenv import load_dotenv

print("Current directory:", os.getcwd())
print("Files in directory:", os.listdir('.'))
print(".env exists?", os.path.exists('.env'))

load_dotenv()

key = os.getenv("GROQ_API_KEY")
if key:
    print(f"✓ Key loaded: {key[:15]}...")
else:
    print("✗ Key NOT loaded")
    print("\nYour .env file should contain:")
    print("GROQ_API_KEY=gsk_yourkey")
    