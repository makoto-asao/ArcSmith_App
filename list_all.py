import google.generativeai as genai
from src.config import Config
import sys

genai.configure(api_key=Config.GEMINI_API_KEY)

print("All available models:", file=sys.stderr)
try:
    models = list(genai.list_models())
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(m.name, file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
