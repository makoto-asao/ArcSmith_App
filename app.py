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
# デフォルトプロンプトの設定 (初回のみ)
DEFAULT_PERSONAS = {
    "marketer": "Viral Architect (YouTube Shortsマーケター): 冒頭1秒の「めくり」と視聴維持率に異常にこだわる。最新のトレンドと海外受けするフックを熟知している。",
    "writer": "The Whisperer (ホラー作家): 言葉の端々に不気味さを漂わせる心理描写の達人。日本特有の「湿り気のある恐怖」を英語の短い台本に昇華させる。",
    "director": "The Visionary (映像監督): Midjourneyを完璧に操る呪文（プロンプト）の魔術師。光の当たり方、レンズ設定(35mm等)、質感(Grainy等)を指定する。"
}

if "persona_prompts" not in st.session_state:
    st.session_state.persona_prompts = DEFAULT_PERSONAS.copy()

# AIGeneratorへのプロンプト同期
def get_persona_str():
    p = st.session_state.persona_prompts
    return f"1. **{p['marketer']}**\n2. **{p['writer']}**\n3. **{p['director']}**"

with st.sidebar:
    st.markdown('<div class="sidebar-logo">ArcSmith</div>', unsafe_allow_html=True)
    
    # プロジェクト状況のタイトル
    st.markdown('<div class="section-header">Current Pipeline Status</div>', unsafe_allow_html=True)
    
    # 後程、非同期っぽく更新するためのプレースホルダー
    status_placeholder = st.empty()
    
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

        with st.expander("🎭 AI Persona Studio", expanded=False):
            st.markdown('<p style="font-size: 0.7rem; color: #94a3b8;">エージェントの性格をカスタマイズできます。</p>', unsafe_allow_html=True)
            st.session_state.persona_prompts["marketer"] = st.text_area("Marketer", st.session_state.persona_prompts["marketer"], height=100)
            st.session_state.persona_prompts["writer"] = st.text_area("Writer", st.session_state.persona_prompts["writer"], height=100)
            st.session_state.persona_prompts["director"] = st.text_area("Director", st.session_state.persona_prompts["director"], height=100)
            if st.button("Reset Personas", use_container_width=True):
                st.session_state.persona_prompts = DEFAULT_PERSONAS.copy()
                st.rerun()

# メインコンテンツエリア
# セッション状態の初期化
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# メインコンテンツエリア
st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > Automated Content Pipeline</p>', unsafe_allow_html=True)

# タブの作成と制御
tab_titles = ["✨ Ideation", "🖋️ Scripting", "🚀 Production"]
tabs = st.tabs(tab_titles)

# ---------------------------------------------------------
# Mode A: Ideation & Selection
# ---------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📝 Mode A: Ideation')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem;">マーケット分析に基づき、バズるネタを5つ提案します。採用するものを1つ選んでください。</p>', unsafe_allow_html=True)
    
    if st.button("Generate New Concepts", use_container_width=True):
        with st.status("👻 分析中...", expanded=False):
            try:
                handler = SheetsHandler()
                existing = handler.get_all_titles()
                ai = AIGenerator()
                ideas_data, full_response = ai.generate_new_ideas(existing)
                st.session_state.new_ideas = list(ideas_data.keys())
                st.session_state.all_ideas_data = ideas_data
                st.session_state.ideation_full = full_response
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

    if "new_ideas" in st.session_state:
        with st.expander("📝 View AI Analysis & Discussion", expanded=False):
            st.markdown(st.session_state.ideation_full)
        
        st.markdown('<p style="font-size: 0.9rem; font-weight: 700;">制作に進めるネタを1つ選択してください：</p>', unsafe_allow_html=True)
        selected_idea = st.radio("Select Idea", st.session_state.new_ideas, label_visibility="collapsed")
        
        if st.button("Adopt this Idea & Proceed to Scripting", use_container_width=True):
            st.session_state.selected_title = selected_idea
            st.session_state.selected_metadata = st.session_state.all_ideas_data.get(selected_idea, {})
            # 自動的にスクリプト生成フラグを立てて、タブを移動
            st.session_state.auto_script = True
            st.info(f"「{selected_idea}」を採択しました。スクリプト生成を開始します...")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Mode B: Scripting & Editorial
# ---------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 🎬 Mode B: Scripting')
    
    # Mode Aからの遷移、または直接開始
    target_title = st.session_state.get("selected_title")
    
    if target_title:
        st.success(f"Selected: **{target_title}**")
        
        # 自動生成フラグがある場合のみ実行
        if st.session_state.get("auto_script"):
            with st.status("🖋️ 台本作成中...", expanded=True):
                try:
                    ai = AIGenerator()
                    res = ai.generate_script_and_prompts(
                        target_title, 
                        context=st.session_state.get("selected_metadata"),
                        expert_persona=get_persona_str()
                    )
                    st.session_state.current_script = res["vrew_script"]
                    st.session_state.current_prompt = res["mj_prompts"]
                    st.session_state.script_full = res["full_text"]
                    st.session_state.auto_script = False # 実行完了
                except Exception as e:
                    st.error(f"Error: {e}")

    if "current_script" in st.session_state:
        with st.expander("📝 View AI Production Notes", expanded=False):
            st.markdown(st.session_state.script_full)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📜 Vrew Script (Editable)**")
            st.session_state.current_script = st.text_area("ScriptArea", st.session_state.current_script, height=400, label_visibility="collapsed")
        with col2:
            st.markdown("**🎨 MJ Prompts (Editable)**")
            st.session_state.current_prompt = st.text_area("PromptArea", st.session_state.current_prompt, height=400, label_visibility="collapsed")
        
        if st.button("Finalize & Publish to Production", key="publish_to_prod", use_container_width=True):
            with st.spinner("Publishing to Sheets..."):
                try:
                    handler = SheetsHandler()
                    # A列に新しい行として追加し、同時にB,C列を書き込む
                    handler.append_new_titles([target_title])
                    # 今追加した行のインデックスを取得（最後尾）
                    all_titles = handler.worksheet.col_values(1)
                    new_row_idx = len(all_titles)
                    handler.update_row_data(new_row_idx, st.session_state.current_script, st.session_state.current_prompt)
                    
                    st.success("Published! Moving to Production...")
                    # データをクリアしてMode Cへ移動
                    st.session_state.production_ready = True
                    st.session_state.prod_title = target_title
                    st.session_state.prod_script = st.session_state.current_script
                    st.session_state.prod_prompt = st.session_state.current_prompt
                    st.session_state.prod_row = new_row_idx
                    
                    del st.session_state.selected_title
                    del st.session_state.current_script
                    st.rerun()
                except Exception as e:
                    st.error(f"Publish failed: {e}")
    else:
        st.warning("Please select an idea in Mode A first.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Mode C: Asset Production
# ---------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown('### 📽️ Mode C: Asset Production')
    
    if st.session_state.get("production_ready"):
        st.success(f"Ready for: **{st.session_state.prod_title}**")
        
        with st.expander("📖 Operation Guide"):
            st.markdown("""
            1. **Launch** ボタンを押すとブラウザが2つ起動します。
            2. **Midjourney**: プロンプトが入力されています。Enterで生成を開始。
            3. **Vrew**: 台本がペーストされています。AIボイスなどを設定して書き出し。
            4. 完了後、**Mark as Complete** ボタンを押してください。
            """)

        if st.button("Launch Production Engines", use_container_width=True):
            try:
                helper_path = os.path.join("src", "automation_helper.py")
                import subprocess
                import sys
                with st.spinner("Kicking off Midjourney & Vrew..."):
                    subprocess.run([sys.executable, helper_path, "mj", st.session_state.prod_prompt], check=True)
                    subprocess.run([sys.executable, helper_path, "vrew", st.session_state.prod_script], check=True)
                st.success("Engines started.")
            except Exception as e:
                st.error(f"Automation Error: {e}")

        if st.button("Mark as Complete & Finish Project", key="mark_final", use_container_width=True):
            handler = SheetsHandler()
            handler.mark_as_completed(st.session_state.prod_row)
            st.snow()
            del st.session_state.production_ready
            st.rerun()
    else:
        # 既存キューからの読み込みも一応サポート
        if st.button("Load Next from Sheets Queue", use_container_width=True):
            handler = SheetsHandler()
            row_idx, row_data = handler.get_unprocessed_row()
            if row_idx and len(row_data) >= 3:
                st.session_state.production_ready = True
                st.session_state.prod_title = row_data[0]
                st.session_state.prod_script = row_data[1]
                st.session_state.prod_prompt = row_data[2]
                st.session_state.prod_row = row_idx
                st.rerun()
            else:
                st.warning("No scripted content found in queue.")

    st.markdown('</div>', unsafe_allow_html=True)

# サイドバー状況の更新（スクリプトの最後で実行することでUIの応答性を確保）
with status_placeholder:
    try:
        with st.spinner("Checking..."):
            handler = SheetsHandler()
            _, row_data = handler.get_unprocessed_row()
            if row_data:
                st.markdown(f'<div class="status-container"><span style="color: #94a3b8; font-size: 0.8rem;">Ready for Production:</span><br/><b style="color: #f8fafc;">{row_data[0]}</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-container" style="color: #10b981;">✅ All processed.</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="status-container" style="color: #ef4444;">Disconnected</div>', unsafe_allow_html=True)
