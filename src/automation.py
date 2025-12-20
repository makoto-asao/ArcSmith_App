import time
import os
import requests
from playwright.sync_api import sync_playwright
from src.auth_manager import AuthManager

class MJAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.url = "https://www.midjourney.com/explore"

    def input_prompt(self, page, prompt):
        """プロンプトを入力して送信する"""
        input_selector = 'textarea[placeholder*="Imagine"], input[placeholder*="Imagine"]'
        page.wait_for_selector(input_selector, timeout=20000)
        page.fill(input_selector, prompt)
        page.keyboard.press("Enter")
        print(f"Midjourney: Prompt sent -> {prompt}")

    def download_latest_image(self, page, download_dir="assets/images"):
        """最新の画像をダウンロードする"""
        os.makedirs(download_dir, exist_ok=True)
        image_selector = 'img[alt*="Imagine"]' 
        page.wait_for_selector(image_selector, timeout=30000)
        img_url = page.eval_on_selector(image_selector, "el => el.src")
        
        if img_url:
            response = requests.get(img_url)
            filename = f"mj_{int(time.time())}.png"
            filepath = os.path.join(download_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Midjourney: Image saved to {filepath}")
            return filepath
        return None

    def generate_and_download_images(self, prompt, download_dir="assets/images"):
        """一連の生成・ダウンロード処理を実行（旧API互換用）"""
        with sync_playwright() as p:
            browser, context = AuthManager.get_context(p, headless=self.headless)
            page = context.new_page()
            page.goto(self.url)
            try:
                self.input_prompt(page, prompt)
                time.sleep(70) # 生成待機
                return self.download_latest_image(page, download_dir)
            except Exception as e:
                print(f"Midjourney Error: {e}")
            finally:
                browser.close()
        return None

class VrewAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.url = "https://vrew.voyagerx.com/ja/"

    def paste_script(self, page, script):
        """Vrewの新規プロジェクトにスクリプトをペーストする"""
        # 1. 「新しく作る」または「テキストからビデオを作成」を探す
        page.wait_for_selector('text="新規で作成する"', timeout=20000)
        page.click('text="新規で作成する"')
        page.wait_for_selector('text="テキストからビデオを作成"', timeout=20000)
        page.click('text="テキストからビデオを作成"')
        
        # 2. スクリプト入力エリアへのペースト
        page.wait_for_selector('textarea', timeout=20000)
        page.fill('textarea', script)
        print("Vrew: Script pasted.")

    def create_video_project(self, script):
        """一連のビデオプロジェクト作成処理を実行（旧API互換用）"""
        with sync_playwright() as p:
            browser, context = AuthManager.get_context(p, headless=self.headless)
            page = context.new_page()
            page.goto(self.url)
            try:
                self.paste_script(page, script)
                time.sleep(5)
            except Exception as e:
                print(f"Vrew Error: {e}")
            finally:
                browser.close()
