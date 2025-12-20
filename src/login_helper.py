import os
import sys
from playwright.sync_api import sync_playwright

def run_login(url, state_path):
    """Playwrightで手動ログインを実行し、セッションを保存する"""
    with sync_playwright() as p:
        # ボット検知を避けるための引数
        args = [
            "--disable-blink-features=AutomationControlled",
        ]
        
        browser = p.chromium.launch(
            headless=False,
            args=args
        )
        
        # ユーザーエージェントなどを本物のブラウザに近づける
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        
        print(f"Opening: {url}")
        page.goto(url)
        
        print("\n" + "="*50)
        print(f" {url} にログインしてください。")
        print(" ※Cloudflareのチェック（「私は人間です」等）が出た場合は、ゆっくり操作してください。")
        print(" 完了したら、ブラウザを閉じてください。")
        print("="*50 + "\n")
        
        # ページが閉じられるのを待つ
        try:
            page.wait_for_event("close", timeout=0) 
        except:
            pass
            
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        context.storage_state(path=state_path)
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python login_helper.py <url> <state_path>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    target_state_path = sys.argv[2]
    run_login(target_url, target_state_path)
