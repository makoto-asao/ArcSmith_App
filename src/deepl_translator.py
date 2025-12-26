import requests
from src.config import Config

class DeepLTranslator:
    def __init__(self):
        self.api_key = Config.DEEPL_API_KEY
        # Free API endpoints usually end with :fx
        if self.api_key.endswith(":fx"):
            self.url = "https://api-free.deepl.com/v2/translate"
        else:
            self.url = "https://api.deepl.com/v2/translate"

    def translate(self, text, target_lang="JA"):
        """Translate text using DeepL API."""
        if not text:
            return ""
        
        params = {
            "auth_key": self.api_key,
            "text": text,
            "target_lang": target_lang
        }
        
        try:
            response = requests.post(self.url, data=params)
            response.raise_for_status()
            result = response.json()
            return result["translations"][0]["text"]
        except Exception as e:
            print(f"DeepL Translation Error: {e}")
            return f"[Translation Error] {text}"
