import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing with API Key starting with: {api_key[:10]}...")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello")
    print("\n[SUCCESS] Google API is working!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"\n[ERROR] Google API failed: {str(e)}")
