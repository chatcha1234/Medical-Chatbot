import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("🔍 Listing available models...")
try:
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"✅ Embedding Model Found: {m.name}")
            print(f"   Description: {m.description}")
        elif 'generateContent' in m.supported_generation_methods:
            print(f"ℹ️  Generation Model: {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
