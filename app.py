import streamlit as st
from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation
from src.config import Config
import os

st.set_page_config(page_title="Jホラー動画制作スタジオ", layout="wide")

st.title("👻 Jホラー動画自動制作システム")

# サイドバー：設定と認証
with st.sidebar:
    st.header("⚙️ 設定")
    gemini_key = st.text_input("Gemini API Key", value=Config.GEMINI_API_KEY or "", type="password")
    if st.button("設定を保存"):
        # .envを更新するロジック（簡易版）
        with open(".env", "a") as f:
            f.write(f"\nGEMINI_API_KEY={gemini_key}")
        st.success("API Keyを保存しました（再起動後に反映）")

    st.header("🔑 認証")
    if st.button("Midjourney ログイン"):
        AuthManager.save_session("https://www.midjourney.com/explore")
    if st.button("Vrew ログイン"):
        AuthManager.save_session("https://vrew.voyagerx.com/ja/")

# メインコンテンツ
tabs = st.tabs(["企画・重複チェック", "台本生成", "動画制作"])

with tabs[0]:
    st.header("📝 モードA: ネタ企画")
    if st.button("新しいネタを5つ生成"):
        try:
            handler = SheetsHandler()
            ai = AIGenerator()
            existing = handler.get_all_titles()
            new_ideas = ai.generate_new_ideas(existing)
            st.write("生成されたネタ:")
            for idea in new_ideas:
                st.write(f"- {idea}")
            if st.button("シートに追加"):
                handler.append_new_titles(new_ideas)
                st.success("シートに追加しました！")
        except Exception as e:
            st.error(f"エラー: {e}")

with tabs[1]:
    st.header("🎬 モードB: 台本・プロンプト生成")
    if st.button("未処理のネタを処理"):
        try:
            handler = SheetsHandler()
            ai = AIGenerator()
            row_idx, row_data = handler.get_unprocessed_row()
            if row_idx:
                title = row_data[0]
                st.info(f"処理中: {title}")
                script, prompt = ai.generate_script_and_prompts(title)
                st.subheader("Vrew用スクリプト")
                st.text_area("Script", script, height=200)
                st.subheader("MJプロンプト")
                st.text_area("Prompt", prompt, height=200)
                
                if st.button("シートに反映"):
                    handler.update_row_data(row_idx, script, prompt)
                    st.success("スプレッドシートを更新しました！")
            else:
                st.warning("未処理のネタが見つかりません。")
        except Exception as e:
            st.error(f"エラー: {e}")

with tabs[2]:
    st.header("📽️ モードC: 自動操作（MJ/Vrew）")
    st.warning("この機能はブラウザが表示された状態で動作します。")
    
    if st.button("未処理のアセット制作を開始"):
        try:
            handler = SheetsHandler()
            row_idx, row_data = handler.get_unprocessed_row()
            
            if row_idx and len(row_data) >= 3 and row_data[1] and row_data[2]:
                title = row_data[0]
                script = row_data[1]
                prompt = row_data[2]
                
                st.info(f"アセット制作開始: {title}")
                
                # 1. Midjourney
                st.subheader("1. Midjourney 画像生成")
                st.info("Midjourneyを起動しています。プロンプトの入力と生成が行われます。")
                helper_path = os.path.join("src", "automation_helper.py")
                try:
                    import subprocess
                    import sys
                    subprocess.run([sys.executable, helper_path, "mj", prompt], check=True)
                    st.success("Midjourneyの操作が完了しました。")
                except Exception as e:
                    st.error(f"Midjourney実行エラー: {e}")
                
                # 2. Vrew
                st.subheader("2. Vrew 動画プロジェクト作成")
                st.info("Vrewを起動して台本を流し込みます。")
                try:
                    subprocess.run([sys.executable, helper_path, "vrew", script], check=True)
                    st.success("Vrewの操作が完了しました。")
                except Exception as e:
                    st.error(f"Vrew実行エラー: {e}")
                
                # 3. 完了フラグ
                st.divider()
                if st.button("すべての制作が完了したとしてマーク"):
                    handler.mark_as_completed(row_idx)
                    st.success("スプレッドシートに完了フラグを書き込みました！")
            else:
                st.warning("台本とプロンプトが用意された未処理のネタが見つかりません。先に「モードB」を実行してください。")
        except Exception as e:
            st.error(f"エラー: {e}")
