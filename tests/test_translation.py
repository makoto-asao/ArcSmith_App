from src.deepl_translator import DeepLTranslator
from src.config import Config

def test_deepl():
    print("=== DeepL API Test Started ===")
    try:
        Config.validate()
        print(f"[OK] Config validation passed. API Key: {Config.DEEPL_API_KEY[:5]}...")
        
        translator = DeepLTranslator()
        test_text = "Beyond this sign the law fades"
        print(f"Translating: '{test_text}'")
        
        result = translator.translate(test_text)
        print(f"Result: '{result}'")
        
        if result and "[Translation Error]" not in result:
            print("[OK] DeepL API is working.")
        else:
            print("[FAIL] Unexpected translation result.")
            
    except Exception as e:
        print(f"[FAIL] DeepL API error: {e}")

if __name__ == "__main__":
    test_deepl()
