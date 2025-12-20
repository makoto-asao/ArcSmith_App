import os
import sys
import subprocess
from src.config import Config

class AuthManager:
    @staticmethod
    def save_session(url, state_path=None):
        """指定したURLで手動ログインし、セッションを保存する（Streamlit互換版）"""
        if not state_path:
            state_path = Config.AUTH_STATE_PATH
        
        # ログインヘルパースクリプトのパス
        helper_path = os.path.join(os.path.dirname(__file__), "login_helper.py")
        
        # subprocessで実行
        print(f"Starting login helper for {url}...")
        try:
            subprocess.run([sys.executable, helper_path, url, state_path], check=True)
            print("Login helper finished successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Login helper failed: {e}")

    @staticmethod
    def get_context(playwright, headless=False):
        """保存されたセッションを使用してブラウザコンテキストを返す"""
        state_path = Config.AUTH_STATE_PATH
        
        # ボット検知を避けるための引数
        args = [
            "--disable-blink-features=AutomationControlled",
        ]
        
        browser = playwright.chromium.launch(
            headless=headless,
            args=args
        )
        
        if os.path.exists(state_path):
            context = browser.new_context(
                storage_state=state_path,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
        else:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            
        return browser, context
