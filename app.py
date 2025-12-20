import streamlit as st
from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation
from src.config import Config
import os

st.set_page_config(
    page_title="ArcSmith | J-Horror AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ITベンチャー・AIスタジオ風の洗練されたCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@300;600;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* タイポグラフィ */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    .main-title {
        font-size: 3.5rem !important;
        background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem !important;
    }

    /* カードスタイル */
    .stCard {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
    }

    /* ボタンのプレミアム化 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4);
        opacity: 0.9;
    }

    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #94a3b8;
        border: none;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
    }

    /* 入力エリア */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">ArcSmith</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; font-size: 1.2rem; margin-top: -1.5rem; margin-bottom: 2.5rem;">The Next Gen J-Horror Production Engine</p>', unsafe_allow_html=True)

# サイドバー：設定と認証
with st.sidebar:
    st.markdown('<h2 style="color: #f8fafc; font-size: 1.5rem; margin-top: 2rem;">System config</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 0.9rem;">API Key & Credentials</p>', unsafe_allow_html=True)
    
    gemini_key = st.text_input("Gemini API Key", value=Config.GEMINI_API_KEY or "", type="password")
    if st.button("Apply Changes", use_container_width=True):
        # .envを更新するロジック（簡易版）
        with open(".env", "a") as f:
            f.write(f"\nGEMINI_API_KEY={gemini_key}")
        st.success("API Key updated.")

    st.markdown('<h2 style="color: #f8fafc; font-size: 1.5rem; margin-top: 2.5rem;">Auth Sessions</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 0.9rem;">Maintain browser sessions</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Midjourney", key="btn_mj"):
            AuthManager.save_session("https://www.midjourney.com/explore")
    with col_b:
        if st.button("Vrew", key="btn_vrew"):
            AuthManager.save_session("https://vrew.voyagerx.com/ja/")

# メインコンテンツ
tabs = st.tabs(["✨ Ideation", "🖋️ Scripting", "🚀 Production"])

with tabs[0]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📝 Mode A: Ideation & Market Research')
    st.markdown('<p style="color: #94a3b8;">呪いの連鎖を断ち切る、新しい恐怖を設計します。</p>', unsafe_allow_html=True)
    
    if st.button("Generate New Concepts", use_container_width=True):
        with st.status("👻 ホラーの深淵を探索中...", expanded=True) as status:
            try:
                st.write("スプレッドシートから既存のデータを分析中...")
                handler = SheetsHandler()
                existing = handler.get_all_titles()
                
                st.write("Gemini 2.5 がバズるネタを構築中...")
                ai = AIGenerator()
                new_ideas = ai.generate_new_ideas(existing)
                
                st.session_state.new_ideas = new_ideas
                status.update(label="✅ Innovation complete", state="complete", expanded=False)
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

    if "new_ideas" in st.session_state:
        st.markdown('<div style="background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1); margin: 1rem 0;">', unsafe_allow_html=True)
        for i, idea in enumerate(st.session_state.new_ideas):
            st.markdown(f"**{i+1}.** {idea}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Commit to Database (Google Sheets)", key="add_to_sheet"):
            with st.spinner("Synchronizing..."):
                handler = SheetsHandler()
                handler.append_new_titles(st.session_state.new_ideas)
                st.success("Database synchronized.")
                del st.session_state.new_ideas
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 🎬 Mode B: Scripting & Visual Concepts')
    st.markdown('<p style="color: #94a3b8;">選定された魂（ネタ）に、言葉と映像の命を吹き込みます。</p>', unsafe_allow_html=True)

    if st.button("Process Unscheduled Content", use_container_width=True):
        with st.status("🖋️ Crafting the narrative...", expanded=True) as status:
            try:
                handler = SheetsHandler()
                row_idx, row_data = handler.get_unprocessed_row()
                if row_idx:
                    title = row_data[0]
                    st.write(f"Analyzing: **{title}**")
                    
                    st.write("AI Director is thinking...")
                    ai = AIGenerator()
                    script, prompt = ai.generate_script_and_prompts(title)
                    
                    st.session_state.current_script = script
                    st.session_state.current_prompt = prompt
                    st.session_state.current_row = row_idx
                    status.update(label=f"✅ Script ready: {title}", state="complete", expanded=False)
                else:
                    st.warning("No unprocessed content found.")
            except Exception as e:
                st.error(f"Error: {e}")

    if "current_script" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📜 Script (Vrew)")
            st.text_area("Script", st.session_state.current_script, height=300, label_visibility="collapsed")
        with col2:
            st.markdown("#### 🎨 Prompts (Midjourney)")
            st.text_area("Prompt", st.session_state.current_prompt, height=300, label_visibility="collapsed")
        
        if st.button("Push to Sheet", key="save_to_sheet"):
            with st.spinner("Updating records..."):
                handler = SheetsHandler()
                handler.update_row_data(st.session_state.current_row, st.session_state.current_script, st.session_state.current_prompt)
                st.success("Asset records updated.")
                del st.session_state.current_script
                del st.session_state.current_prompt
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📽️ Mode C: Automated Asset Production')
    st.markdown('<p style="color: #94a3b8;">Midjourney と Vrew を同期し、最終アセットを錬成します。</p>', unsafe_allow_html=True)
    
    if st.button("Launch Full Production Pipeline", use_container_width=True):
        try:
            handler = SheetsHandler()
            row_idx, row_data = handler.get_unprocessed_row()
            
            if row_idx and len(row_data) >= 3 and row_data[1] and row_data[2]:
                title = row_data[0]
                script = row_data[1]
                prompt = row_data[2]
                
                st.markdown(f"**Target:** {title}")
                
                with st.status("🎨 Generation in progress (Midjourney)", expanded=True) as s1:
                    helper_path = os.path.join("src", "automation_helper.py")
                    import subprocess
                    import sys
                    subprocess.run([sys.executable, helper_path, "mj", prompt], check=True)
                    s1.update(label="✅ Imaging complete", state="complete")
                
                with st.status("🎬 Assembling project (Vrew)", expanded=True) as s2:
                    subprocess.run([sys.executable, helper_path, "vrew", script], check=True)
                    s2.update(label="✅ Video project established", state="complete")
                
                st.divider()
                st.success("Pipeline tasks completed. Please finalize in your browser.")
                if st.button("Mark as Published", key="mark_final"):
                    handler.mark_as_completed(row_idx)
                    st.snow()
            else:
                st.warning("No ready-to-produce content found.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
