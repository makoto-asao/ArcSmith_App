import streamlit as st
from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation
from src.config import Config
import os

st.set_page_config(page_title="Jホラー動画制作スタジオ", layout="wide")

# カスタムCSSでホラー感を演出
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #ff4b4b;
        background-color: #1e1e1e;
        color: #ff4b4b;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b;
        color: white;
        box-shadow: 0 0 15px #ff4b4b;
    }
    h1 {
        color: #ff4b4b;
        text-shadow: 2px 2px 5px black;
    }
</style>
""", unsafe_allow_html=True)

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
    
    if st.button("✨ 新しいネタを5つ生成", use_container_width=True):
        with st.status("👻 ホラーの深淵を探索中...", expanded=True) as status:
            try:
                st.write("スプレッドシートから既存の呪いを読み込み中...")
                handler = SheetsHandler()
                existing = handler.get_all_titles()
                
                st.write("Geminiが新しい恐怖を考案中...")
                ai = AIGenerator()
                new_ideas = ai.generate_new_ideas(existing)
                
                st.session_state.new_ideas = new_ideas
                status.update(label="✅ 5つの新しい怪談が誕生しました", state="complete", expanded=False)
                st.balloons()
            except Exception as e:
                st.error(f"エラー: {e}")

    if "new_ideas" in st.session_state:
        st.subheader("💀 生成されたネタ")
        for i, idea in enumerate(st.session_state.new_ideas):
            st.markdown(f"**{i+1}.** {idea}")
        
        if st.button("📂 スプレッドシートに魂を刻む（追加）", key="add_to_sheet"):
            with st.spinner("シートを更新中..."):
                handler = SheetsHandler()
                handler.append_new_titles(st.session_state.new_ideas)
                st.success("スプレッドシートへの追記が完了しました。")
                del st.session_state.new_ideas

with tabs[1]:
    st.header("🎬 モードB: 台本・プロンプト生成")
    if st.button("👁️ 未処理のネタを脚本化する", use_container_width=True):
        with st.status("🖋️ 脚本を執筆中...", expanded=True) as status:
            try:
                handler = SheetsHandler()
                row_idx, row_data = handler.get_unprocessed_row()
                if row_idx:
                    title = row_data[0]
                    st.write(f"対象ネタ: **{title}**")
                    
                    st.write("Geminiがビデオ構成と画像案を構築中...")
                    ai = AIGenerator()
                    script, prompt = ai.generate_script_and_prompts(title)
                    
                    st.session_state.current_script = script
                    st.session_state.current_prompt = prompt
                    st.session_state.current_row = row_idx
                    status.update(label=f"✅ 『{title}』の脚本が完成しました", state="complete", expanded=False)
                    st.toast("台本生成完了！")
                else:
                    st.warning("未処理のネタが見つかりません。")
            except Exception as e:
                st.error(f"エラー: {e}")

    if "current_script" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📜 Vrew用スクリプト")
            st.text_area("Script", st.session_state.current_script, height=300)
        with col2:
            st.subheader("🎨 Midjourneyプロンプト")
            st.text_area("Prompt", st.session_state.current_prompt, height=300)
        
        if st.button("💾 この内容をシートに封印する", key="save_to_sheet"):
            with st.spinner("保存中..."):
                handler = SheetsHandler()
                handler.update_row_data(st.session_state.current_row, st.session_state.current_script, st.session_state.current_prompt)
                st.success("スプレッドシートに書き込みました。")
                del st.session_state.current_script
                del st.session_state.current_prompt

with tabs[2]:
    st.header("📽️ モードC: 自動操作（MJ/Vrew）")
    st.warning("この機能はブラウザが表示された状態で動作します。")
    
    if st.button("🚀 未処理のアセット制作を開始（MJ & Vrew）", use_container_width=True):
        try:
            handler = SheetsHandler()
            row_idx, row_data = handler.get_unprocessed_row()
            
            if row_idx and len(row_data) >= 3 and row_data[1] and row_data[2]:
                title = row_data[0]
                script = row_data[1]
                prompt = row_data[2]
                
                st.subheader(f"🕯️ 現在の制作対象: {title}")
                
                # 1. Midjourney
                with st.status("🎨 Midjourneyで画像生成中...", expanded=True) as status:
                    st.write("Midjourneyを起動中...")
                    helper_path = os.path.join("src", "automation_helper.py")
                    try:
                        import subprocess
                        import sys
                        st.write("プロンプトを入力しています...")
                        subprocess.run([sys.executable, helper_path, "mj", prompt], check=True)
                        status.update(label="✅ Midjourneyの操作が完了しました", state="complete")
                    except Exception as e:
                        st.error(f"Midjourney実行エラー: {e}")
                
                # 2. Vrew
                with st.status("🎬 Vrewで動画プロジェクト作成中...", expanded=True) as status:
                    st.write("Vrewを起動中...")
                    try:
                        st.write("スクリプトを流し込んでいます...")
                        subprocess.run([sys.executable, helper_path, "vrew", script], check=True)
                        status.update(label="✅ Vrewの操作が完了しました", state="complete")
                    except Exception as e:
                        st.error(f"Vrew実行エラー: {e}")
                
                # 3. 完了フラグ
                st.divider()
                st.success("全ての自動操作が一旦終了しました。ブラウザでの最終確認をお願いします。")
                if st.button("👿 全ての制作を完了とし、シートに刻む", key="mark_final"):
                    handler.mark_as_completed(row_idx)
                    st.success("スプレッドシートを『完了』に更新しました。")
                    st.snow()
            else:
                st.warning("対象となる未処理データが見つかりません。")
        except Exception as e:
            st.error(f"エラー: {e}")
