import google.generativeai as genai
import os

# Manual config if .env fails
api_key = "PASTE_KEY_HERE" # Not safe, I'll use the one from src/config.py
try:
    from src.config import Config
    api_key = Config.GEMINI_API_KEY
except:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: API Key not found")
else:
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            print(f"{m.name}")
    except Exception as e:
        print(f"Exception: {e}")
