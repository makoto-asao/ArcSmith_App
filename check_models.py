import google.generativeai as genai
from src.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

print("Available models that support generateContent:")
print("-" * 60)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Name: {m.name}")
        print(f"  Display: {m.display_name}")
        print(f"  Methods: {m.supported_generation_methods}")
        print()
