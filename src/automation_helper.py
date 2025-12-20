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
    mj = MJAutomation(headless=False)
    vrew = VrewAutomation(headless=False)

    with sync_playwright() as p:
        if mode == 'mj':
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto(mj.url)
            
            try:
                print("\n" + "!"*50)
                print(" Midjourney 操作ガイド:")
                print(" 1. プロンプトは自動で入力されました。Enter を押して生成を開始してください。")
                print(" 2. 生成が終わるまで約1分待ちます。")
                print(" 3. 気に入った画像の [U1]〜[U4] ボタンを押し、高解像度化（Upscale）してください。")
                print(" 4. 高解像度化された画像をクリックし、左下の「Download」アイコンで保存してください。")
                print(" 5. すべて終わったら、このブラウザを閉じてください。")
                print("!"*50 + "\n")
                
                mj.input_prompt(page, data)
                page.wait_for_event("close", timeout=0)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                browser.close()

        elif mode == 'vrew':
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto(vrew.url)
            
            try:
                print("\n" + "!"*50)
                print(" Vrew 操作ガイド:")
                print(" 1. 台本は自動でペーストされました。")
                print(" 2. 音声モデル（AI Voice）や BGM を選択し、プロジェクトを完成させてください。")
                print(" 3. 必要に応じて「書き出し」を行ってください。")
                print(" 4. 作業が終わったら、このブラウザを閉じてください。")
                print("!"*50 + "\n")
                
                vrew.paste_script(page, data)
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
