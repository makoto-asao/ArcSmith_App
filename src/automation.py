import time
import os
from playwright.sync_api import sync_playwright
from src.auth_manager import AuthManager

class MJAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.url = "https://www.midjourney.com/explore"

    def input_prompt(self, page, prompt):
        """プロンプトを入力して送信する（複数プロンプト対応）"""
        try:
            # MJの入力エリアを探す
            input_selectors = [
                'p[data-placeholder*="Prompt"]',
                'textarea[placeholder*="Imagine"]',
                'input[placeholder*="Imagine"]',
                'div[role="textbox"]',
                'textarea'
            ]
            
            target_selector = None
            for selector in input_selectors:
                try:
                    page.wait_for_selector(selector, timeout=3000)
                    target_selector = selector
                    break
                except:
                    continue
            
            if not target_selector:
                raise Exception("Could not find Midjourney prompt input field.")
            
            # プロンプトをリスト化（改行区切りまたは単一文字列）
            prompts = prompt.split("\n") if isinstance(prompt, str) else prompt
            prompts = [p.strip() for p in prompts if p.strip()]

            for p_text in prompts:
                # 入力エリアをクリックしてフォーカス
                page.click(target_selector)
                
                # /imagine コマンドを打つ
                page.keyboard.type("/imagine", delay=50)
                page.keyboard.press("Enter")
                time.sleep(1)
                
                # 生成プロンプトを打つ
                page.keyboard.type(p_text, delay=30) 
                page.keyboard.press("Enter")
                
                print(f"Midjourney: Prompt sent -> {p_text[:50]}...")
                time.sleep(5) # 連続投入による詰まりを避けるためのウェイト
            
        except Exception as e:
            print(f"Midjourney Input Error: {e}")
            raise e

    def download_latest_image(self, page, download_dir="assets/images"):
        """最新の画像をダウンロードする（セッション維持のためブラウザコンテキストを使用）"""
        os.makedirs(download_dir, exist_ok=True)
        # より確実なセレクタ：生成完了後に表示される画像
        image_selector = 'img[alt*="Imagine"], img[src*="cdn.midjourney.com"]' 
        try:
            page.wait_for_selector(image_selector, timeout=30000)
            img_url = page.eval_on_selector(image_selector, "el => el.src")
            
            if img_url:
                # requestsの代わりにbrowser contextのrequestを使用してCookie/Authを維持
                response = page.request.get(img_url)
                if response.status == 200:
                    content_type = response.headers.get("content-type", "")
                    if "image" not in content_type:
                        print(f"Warning: Downloaded content is not an image ({content_type})")
                        return None
                        
                    filename = f"mj_{int(time.time())}.png"
                    filepath = os.path.join(download_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(response.body())
                    print(f"Midjourney: Image saved to {filepath}")
                    return filepath
                else:
                    print(f"Midjourney Download Failed: HTTP {response.status}")
        except Exception as e:
            print(f"Midjourney Download Error: {e}")
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

    def paste_script(self, page, script, style_name="情報の伝達", aspect_ratio="16:9"):
        """Vrewの新規プロジェクトにスクリプトをペーストし、スタイルを選択する"""
        try:
            # 1. 「新規で作成する」ボタンを探す
            page.wait_for_load_state("networkidle")
            create_btn_selector = 'button:has-text("新規で作成する"), button:has-text("Create New")'
            page.wait_for_selector(create_btn_selector, timeout=30000)
            page.click(create_btn_selector)
            
            # 2. 「テキストからビデオを作成」を選択
            text_to_video_selector = 'div:has-text("テキストからビデオを作成"), button:has-text("テキストからビデオを作成")'
            page.wait_for_selector(text_to_video_selector, timeout=20000)
            page.click(text_to_video_selector)

            # 3. アスペクト比の選択 (YouTube, Shortなど)
            # 例: [alt="YouTube"] のようなセレクタやテキストを探す
            ratio_selector = f'div:has-text("{aspect_ratio}"), button:has-text("{aspect_ratio}")'
            try:
                page.wait_for_selector(ratio_selector, timeout=5000)
                page.click(ratio_selector)
                # 「次へ」ボタン
                page.click('button:has-text("次へ"), button:has-text("Next")')
            except:
                print(f"Vrew: Aspect ratio {aspect_ratio} already selected or not found.")

            # 4. スタイル選択
            # 指定されたスタイル名を探してクリック
            style_selector = f'div:has-text("{style_name}"), p:has-text("{style_name}")'
            try:
                page.wait_for_selector(style_selector, timeout=10000)
                page.click(style_selector)
                print(f"Vrew: Selected style -> {style_name}")
                # 「次へ」ボタン
                page.click('button:has-text("次へ"), button:has-text("Next")')
            except:
                print(f"Vrew: Style {style_name} not found. Proceeding with default.")

            # 5. スクリプトの入力
            st_textarea = 'textarea[placeholder*="入力"], textarea[placeholder*="script"], textarea'
            page.wait_for_selector(st_textarea, timeout=30000)
            page.fill(st_textarea, "")
            page.fill(st_textarea, script)
            
            print("Vrew: Script successfully pasted into the editor.")
            
        except Exception as e:
            print(f"Vrew Automation Error: Detailed Step Failure - {e}")
            raise e

    def create_video_project(self, script):
        """一連のビデオプロジェクト作成処理を実行（旧API互換用）"""
        with sync_playwright() as p:
            browser, context = AuthManager.get_context(p, headless=self.headless)
            page = context.new_page()
            page.goto(self.url)
            try:
                self.paste_script(page, script)
                # ユーザーが確認できるように少し待つ
                time.sleep(5)
            except Exception as e:
                print(f"Vrew sequence failed: {e}")
            finally:
                browser.close()
