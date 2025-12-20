import sys
import os
import time
from playwright.sync_api import sync_playwright
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation

def run_production(mode, data):
    """
    mode: 'mj' or 'vrew'
    data: prompt (for mj) or script (for vrew)
    """
    with sync_playwright() as p:
        if mode == 'mj':
            mj = MJAutomation(headless=False)
            # MJAutomationクラス内のロジックをここで実行するか、クラスを呼び出す
            # 現状のMJAutomationは内部でsync_playwrightを呼んでいるので、二重にならないよう注意が必要
            # ここではシンプルに直接実行するロジックを記述
            
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto("https://www.midjourney.com/explore")
            
            try:
                # プロンプト入力
                input_selector = 'textarea[placeholder*="Imagine"], input[placeholder*="Imagine"]'
                page.wait_for_selector(input_selector, timeout=20000)
                page.fill(input_selector, data)
                page.keyboard.press("Enter")
                print(f"Midjourney: Prompt sent")
                
                # 生成完了を待つ（手動で確認してもらうために長めに待機するか、page.pause()する）
                print("生成が終わるまでお待ちください。完了したらブラウザを閉じてください。")
                page.wait_for_event("close", timeout=0)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                browser.close()

        elif mode == 'vrew':
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto("https://vrew.voyagerx.com/ja/")
            
            try:
                # Vrewの操作
                page.wait_for_selector('text="新規で作成する"', timeout=20000)
                page.click('text="新規で作成する"')
                page.click('text="テキストからビデオを作成"')
                
                # スクリプト入力
                page.wait_for_selector('textarea', timeout=20000)
                page.fill('textarea', data)
                
                print("Vrew: Script pasted. ブラウザを閉じて完了してください。")
                page.wait_for_event("close", timeout=0)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    cmd_mode = sys.argv[1]
    cmd_data = sys.argv[2]
    run_production(cmd_mode, cmd_data)
