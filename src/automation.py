import time
import os
import requests
from playwright.sync_api import sync_playwright
from src.auth_manager import AuthManager

class MJAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.url = "https://www.midjourney.com/explore"

    def generate_and_download_images(self, prompt, download_dir="assets/images"):
        """プロンプトを入力して生成し、画像をダウンロードする"""
        os.makedirs(download_dir, exist_ok=True)
        
        with sync_playwright() as p:
            browser, context = AuthManager.get_context(p, headless=self.headless)
            page = context.new_page()
            page.goto(self.url)
            
            try:
                # 1. プロンプト入力フィールドを探して入力
                input_selector = 'textarea[placeholder*="Imagine"], input[placeholder*="Imagine"]'
                page.wait_for_selector(input_selector, timeout=20000)
                page.fill(input_selector, prompt)
                page.keyboard.press("Enter")
                print(f"Midjourney: Prompt sent -> {prompt}")
                
                # 2. 生成開始の待機（簡易的に待つか、要素の変化を監視）
                # MJ Alpha版は生成中の画像がリストの先頭に出る
                time.sleep(10) # 処理開始を待つ
                
                # 3. 生成完了の待機（最大3分）
                print("Midjourney: Waiting for generation...")
                time.sleep(60) 
                
                # 4. 最新の画像（U1など）を取得してダウンロード
                # 注: MJ Web版の最新のDOM構造に依存するため、ここは柔軟なセレクタが必要
                # 一旦、ページの最初の画像要素を取得する試行
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
                
            except Exception as e:
                print(f"Midjourney Error: {e}")
            finally:
                browser.close()
        return None

class VrewAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.url = "https://vrew.voyagerx.com/ja/"

    def create_video_project(self, script):
        """Vrewで新規プロジェクトを作成し、スクリプトを入力する"""
        with sync_playwright() as p:
            browser, context = AuthManager.get_context(p, headless=self.headless)
            page = context.new_page()
            page.goto(self.url)
            
            try:
                # 1. 「新しく作る」または「テキストからビデオを作成」を探す
                # VrewのUIは頻繁に変わるため、テキストで探すのが安全
                page.click('text="新規で作成する"', timeout=10000)
                page.click('text="テキストからビデオを作成"', timeout=10000)
                
                # 2. スクリプト入力エリアへのペースト
                # テキストエリアを見つけて入力
                page.wait_for_selector('textarea', timeout=10000)
                page.fill('textarea', script)
                
                print("Vrew: Script pasted. Please complete the rest manually (Voice/BGM selection).")
                # ここでポーズしてユーザーに確認させるか、そのままセッションを閉じずにおく
                time.sleep(5) 
                
            except Exception as e:
                print(f"Vrew Error: {e}")
            finally:
                # Vrewは操作途中でブラウザを閉じると作業が消える場合があるため、
                # headless=False の場合は閉じずに残すのも手だが、一旦閉じる設計
                browser.close()
