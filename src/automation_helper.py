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
                mj.input_prompt(page, data)
                print("生成が終わるまでお待ちください。完了したらブラウザを閉じてください。")
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
                vrew.paste_script(page, data)
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
