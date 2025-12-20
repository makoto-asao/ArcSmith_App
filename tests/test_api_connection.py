from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.config import Config
import sys

def test_connections():
    print("=== Connection Test Started ===")
    
    # 1. Config Check
    try:
        Config.validate()
        print("[OK] Config validation passed.")
    except Exception as e:
        print(f"[FAIL] Config error: {e}")
        return

    # 2. Google Sheets Check
    try:
        handler = SheetsHandler()
        titles = handler.get_all_titles()
        print(f"[OK] Connected to Google Sheets. Found {len(titles)} titles.")
    except Exception as e:
        print(f"[FAIL] Google Sheets error: {e}")

    # 3. Gemini API Check
    try:
        gen = AIGenerator()
        test_ideas = gen.generate_new_ideas(["テストネタ1"])
        print(f"[OK] Gemini API is working. Generated ideas: {test_ideas}")
    except Exception as e:
        print(f"[FAIL] Gemini API error: {e}")

if __name__ == "__main__":
    test_connections()
