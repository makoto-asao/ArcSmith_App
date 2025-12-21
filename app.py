import streamlit as st
from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation
from src.config import Config
import os

st.set_page_config(
    page_title="ArcSmith | Production Console",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ArcSmith Editorial Production Console - Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono&display=swap');

    /* --- Core Layout & Typography --- */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #0f172a;
        line-height: 1.6;
    }

    /* --- Application Header --- */
    [data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #e2e8f0;
        height: 3.5rem !important;
    }
    [data-testid="stHeader"] svg { fill: #0f172a !important; }
    [data-testid="stHeader"] button { background: transparent !important; color: #0f172a !important; }

    /* --- Sidebar Console --- */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Text Color in Dark Sidebar */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b,
    [data-testid="stSidebar"] div[data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] .section-header {
        color: #f8fafc !important;
    }

    /* Sidebar Controls (Collapse/Expand) - Visibility Failsafe */
    [data-testid="stSidebarCollapseButton"] button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: #ffffff !important;
    }

    /* Responsive Icon Color Toggle (White on Blue / Black on White) */
    [data-testid="stSidebarCollapseButton"] button * {
        color: #ffffff !important;
        fill: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="collapsedControl"] button * {
        color: #0f172a !important;
        fill: #0f172a !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    .sidebar-logo {
        font-weight: 800; font-size: 1.8rem; color: #ffffff;
        letter-spacing: -0.05em; padding: 1rem 0 1.5rem 1rem;
    }
    .status-container {
        padding: 1rem; margin: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* --- Content Components --- */
    .stCard {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
    }

    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; padding: 0; margin-bottom: 2rem; }
    .stTabs [data-baseweb="tab"] {
        height: 44px; border-radius: 10px; font-weight: 600;
        background-color: #f1f5f9; color: #64748b;
        padding: 0 24px; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important; color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }

    /* Professional Buttons */
    .stButton>button {
        border-radius: 10px; font-weight: 700; padding: 0.7rem 1.5rem;
        border: 2px solid #0f172a; background: #0f172a; color: #ffffff;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: #334155; border-color: #334155;
        color: #ffffff; transform: translateY(-2px);
    }

    /* High-Legibility Input Fields */
    .stTextArea textarea, .stTextInput input {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #0f172a !important; box-shadow: 0 0 0 1px #0f172a !important;
    }

    /* Section Typography */
    .section-header {
        font-size: 0.75rem; font-weight: 800; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.15rem; margin-bottom: 0.6rem;
    }
    h3 { font-weight: 800 !important; letter-spacing: -0.02em; }
    strong { color: #1e40af; }
    
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# サイドバー：ナビゲーションと設定
with st.sidebar:
    st.markdown('<div class="sidebar-logo">ArcSmith</div>', unsafe_allow_html=True)
    
    # プロジェクト状況のサマリー
    st.markdown('<div class="section-header">Current Pipeline Status</div>', unsafe_allow_html=True)
    handler = SheetsHandler()
    try:
        _, row_data = handler.get_unprocessed_row()
        if row_data:
            st.markdown(f'<div class="status-container"><span style="color: #94a3b8; font-size: 0.8rem;">Ready for Production:</span><br/><b style="color: #f8fafc;">{row_data[0]}</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-container" style="color: #10b981;">✅ All rows processed.</div>', unsafe_allow_html=True)
    except:
        st.error("Sheets connection failed.")

    st.divider()
    
    with st.expander("⚙️ System Configuration"):
        gemini_key = st.text_input("Gemini API Key", value=Config.GEMINI_API_KEY or "", type="password")
        if st.button("Update Key", use_container_width=True):
            env_lines = []
            if os.path.exists(".env"):
                with open(".env", "r", encoding="utf-8") as f:
                    env_lines = f.readlines()
            
            updated = False
            with open(".env", "w", encoding="utf-8") as f:
                for line in env_lines:
                    if line.startswith("GEMINI_API_KEY="):
                        f.write(f"GEMINI_API_KEY={gemini_key}\n")
                        updated = True
                    else:
                        f.write(line)
                if not updated:
                    if env_lines and not env_lines[-1].endswith("\n"):
                        f.write("\n")
                    f.write(f"GEMINI_API_KEY={gemini_key}\n")
            st.success("API Key updated.")

        st.markdown('<p style="font-size: 0.8rem; margin-top: 1rem;">Auth Sessions</p>', unsafe_allow_html=True)
        col_mj, col_vr = st.columns(2)
        with col_mj:
            if st.button("MJ Auth", key="sidebar_mj"):
                AuthManager.save_session("https://www.midjourney.com/explore")
        with col_vr:
            if st.button("Vrew Auth", key="sidebar_vrew"):
                AuthManager.save_session("https://vrew.voyagerx.com/ja/")

# メインコンテンツエリア
st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > Automated Content Pipeline</p>', unsafe_allow_html=True)

tabs = st.tabs(["✨ Ideation", "🖋️ Scripting", "🚀 Production"])

with tabs[0]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📝 Mode A: Ideation')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem;">マーケット分析に基づき、バズるネタを自動生成します。</p>', unsafe_allow_html=True)
    
    if st.button("Generate New Concepts", use_container_width=True):
        with st.status("👻 分析中...", expanded=False):
            try:
                handler = SheetsHandler()
                existing = handler.get_all_titles()
                ai = AIGenerator()
                new_ideas, full_response = ai.generate_new_ideas(existing)
                st.session_state.new_ideas = new_ideas
                st.session_state.ideation_full = full_response
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

    if "new_ideas" in st.session_state:
        st.markdown('<div style="background: rgba(0,0,0,0.3); padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; border: 1px solid #334155;">', unsafe_allow_html=True)
        st.markdown(st.session_state.ideation_full)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Push to Database", key="add_to_sheet"):
            with st.spinner("Syncing..."):
                handler = SheetsHandler()
                handler.append_new_titles(st.session_state.new_ideas)
                st.success("Synced to Sheets.")
                del st.session_state.new_ideas
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 🎬 Mode B: Scripting')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem;">未処理のネタを台本と画像プロンプトに変換します。</p>', unsafe_allow_html=True)

    if st.button("Process Unscheduled Content", use_container_width=True):
        with st.status("🖋️ 台本作成中...", expanded=False):
            try:
                handler = SheetsHandler()
                row_idx, row_data = handler.get_unprocessed_row()
                if row_idx:
                    ai = AIGenerator()
                    res = ai.generate_script_and_prompts(row_data[0])
                    st.session_state.current_script = res["vrew_script"]
                    st.session_state.current_prompt = res["mj_prompts"]
                    st.session_state.script_full = res["full_text"]
                    st.session_state.current_row = row_idx
                else:
                    st.warning("No unprocessed items.")
            except Exception as e:
                st.error(f"Error: {e}")

    if "current_script" in st.session_state:
        st.markdown(f"#### 🎬 Details: {row_data[0]}")
        st.info(st.session_state.script_full)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📜 Vrew Script**")
            st.text_area("ScriptArea", st.session_state.current_script, height=300, label_visibility="collapsed")
        with col2:
            st.markdown("**🎨 MJ Prompts**")
            st.text_area("PromptArea", st.session_state.current_prompt, height=300, label_visibility="collapsed")
        
        if st.button("Finalize & Save to Database", key="save_to_sheet"):
            with st.spinner("Updating..."):
                handler = SheetsHandler()
                handler.update_row_data(st.session_state.current_row, st.session_state.current_script, st.session_state.current_prompt)
                st.success("Saved.")
                del st.session_state.current_script
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📽️ Mode C: Asset Production')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem;">ブラウザ自動化により、制作プロセスをキックオフします。</p>', unsafe_allow_html=True)
    
    with st.expander("📖 Operation Guide"):
        st.markdown("""
        1. **Launch** ボタンを押すとブラウザが2つ起動します。
        2. **Midjourney**: プロンプトが入力されています。Enterで生成を開始。
        3. **Vrew**: 台本がペーストされています。AIボイスなどを設定して書き出し。
        4. 完了後、アプリに戻り **Publish** ボタンを押してください。
        """)

    if st.button("Launch Full Production Pipeline", use_container_width=True):
        try:
            handler = SheetsHandler()
            row_idx, row_data = handler.get_unprocessed_row()
            if row_idx and len(row_data) >= 3 and row_data[1] and row_data[2]:
                title, script, prompt = row_data[0], row_data[1], row_data[2]
                st.markdown(f"**Current Pipeline Target:** {title}")
                
                helper_path = os.path.join("src", "automation_helper.py")
                import subprocess
                import sys
                with st.spinner("Launching Automation Engines..."):
                    subprocess.run([sys.executable, helper_path, "mj", prompt], check=True)
                    subprocess.run([sys.executable, helper_path, "vrew", script], check=True)
                
                st.success("Workflow kicked off. Please finalize in the browser.")
                if st.button("Mark as Published", key="mark_final"):
                    handler.mark_as_completed(row_idx)
                    st.snow()
            else:
                st.warning("No scripted content found to produce.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
