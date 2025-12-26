import sys
import os
import time
from playwright.sync_api import sync_playwright

def run_production(mode, path, style="情報の伝達", ratio="16:9"):
    """
    mode: 'mj' or 'vrew'
    path: Path to the temp file containing prompt or script
    """
    print(f"--- Production Engine Started ---")
    print(f"Mode: {mode}")
    print(f"Data Path: {path}")
    if mode == 'vrew':
        print(f"Style: {style}, Ratio: {ratio}")
    print(f"Time: {time.ctime()}")

    if not os.path.exists(path):
        print(f"Error: Temporary file not found at {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        print(f"Successfully loaded data. Length: {len(data)} characters.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    try:
        from src.auth_manager import AuthManager
        from src.automation import MJAutomation, VrewAutomation
    except ImportError as ie:
        print(f"Import Error: {ie}")
        print(f"Current Path: {os.getcwd()}")
        print(f"Sys Path: {sys.path}")
        input("\nPress Enter to close...") # ウィンドウを閉じないようにする
        return

    mj = MJAutomation(headless=False)
    vrew = VrewAutomation(headless=False)

    with sync_playwright() as p:
        from src.config import Config
        state_path = Config.AUTH_STATE_PATH
        
        if mode == 'mj':
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto(mj.url)
            
            try:
                print("\n" + "!"*50)
                print(" Midjourney 操作ガイド:")
                print(" 1. 複数のプロンプトが順次送信されます。")
                print(" 2. 全プロンプトの送信が終わるまでブラウザを閉じないでください。")
                print(" 3. 必要に応じて [U1]〜[U4] ボタンで高解像度化してください。")
                print(" 4. 作業が終わったら、このブラウザを閉じてください。")
                print("!"*50 + "\n")
                
                mj.input_prompt(page, data)
                page.wait_for_event("close", timeout=0)
            except Exception as e:
                print(f"Error: {e}")
                input("\nPress Enter to close...")
            finally:
                # 終了前にセッションを保存
                os.makedirs(os.path.dirname(state_path), exist_ok=True)
                context.storage_state(path=state_path)
                browser.close()

        elif mode == 'vrew':
            browser, context = AuthManager.get_context(p, headless=False)
            page = context.new_page()
            page.goto(vrew.url)
            
            try:
                print("\n" + "!"*50)
                print(" Vrew 操作ガイド:")
                print(f" 1. スタイル「{style}」アスペクト比「{ratio}」を自動選択します。")
                print(" 2. 台本は自動でペーストされます。")
                print(" 3. 設定が終わったら、必要に応じて「書き出し」を行ってください。")
                print(" 4. 全て終わったら、このブラウザを閉じてください。")
                print("!"*50 + "\n")
                
                vrew.paste_script(page, data, style_name=style, aspect_ratio=ratio)
                page.wait_for_event("close", timeout=0)
            except Exception as e:
                print(f"Error: {e}")
                input("\nPress Enter to close...")
            finally:
                # 終了前にセッションを保存
                os.makedirs(os.path.dirname(state_path), exist_ok=True)
                context.storage_state(path=state_path)
                browser.close()

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("Usage: python automation_helper.py <mode> <path> [style] [ratio]")
            time.sleep(5)
            sys.exit(1)
        
        cmd_mode = sys.argv[1]
        cmd_path = sys.argv[2]
        cmd_style = sys.argv[3] if len(sys.argv) > 3 else "情報の伝達"
        cmd_ratio = sys.argv[4] if len(sys.argv) > 4 else "16:9"
        
        print(f"--- [ArcSmith Engine] Initializing {cmd_mode} mode ---")
        run_production(cmd_mode, cmd_path, style=cmd_style, ratio=cmd_ratio)
        
    except Exception as e:
        print("\n" + "#"*60)
        print(f" FATAL ERROR in automation_helper.py:")
        print(f" {e}")
        import traceback
        traceback.print_exc()
        print("#"*60 + "\n")
        input("Press Enter to close this window...")
    
    finally:
        print("\n--- [ArcSmith Engine] Process finished ---")
        # 成功時も確認のために少し待つか、入力を待つ
        time.sleep(3)
