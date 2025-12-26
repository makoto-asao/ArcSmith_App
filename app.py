import streamlit as st
from src.sheets_handler import SheetsHandler
from src.ai_generator import AIGenerator
from src.auth_manager import AuthManager
from src.automation import MJAutomation, VrewAutomation
from src.config import Config
from src.draft_manager import DraftManager
import os
import pyperclip
import time

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

    /* Forging Glow Animation */
    @keyframes forge-glow {
        0% { box-shadow: 0 0 0 0 rgba(15, 23, 42, 0); transform: translateY(0); }
        50% { box-shadow: 0 0 30px 10px rgba(15, 23, 42, 0.15); transform: translateY(-5px); }
        100% { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); transform: translateY(0); }
    }
    .forge-animation {
        animation: forge-glow 1.5s ease-out forwards;
    }
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

if "current_page" not in st.session_state:
    st.session_state.current_page = "Production Console"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3-flash-preview"

# AIGeneratorへのプロンプト同期
def get_persona_str():
    p = st.session_state.persona_prompts
    return f"1. **{p['marketer']}**\n2. **{p['writer']}**\n3. **{p['director']}**"

# --- Navigation Controller (Runs before UI) ---
# 1. ユーザーによる直接操作（ウィジェット更新）をセッション状態に同期
if "main_nav_radio" in st.session_state:
    st.session_state.current_page = st.session_state.main_nav_radio

# 2. プログラムによる強制遷移（保留中のリクエスト）を処理
if "page_to_redirect" in st.session_state:
    target_page = st.session_state.page_to_redirect
    st.session_state.current_page = target_page
    # ウィジェットの状態も強制的に上書きすることで、次回描画時に確実に反映させる
    st.session_state["main_nav_radio"] = target_page
    del st.session_state.page_to_redirect

if "tab_to_redirect" in st.session_state:
    st.session_state.active_tab = st.session_state.tab_to_redirect
    del st.session_state.tab_to_redirect

with st.sidebar:
    st.logo("assets/logo.png", size="large")
    
    # ナビゲーション
    st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
    
    # ページリスト
    pages = ["Production Console", "📋 Draft List", "🎭 AI Persona Studio", "⚙️ System Configuration"]
    
    # current_pageが設定されている場合、対応するindexを取得
    if "current_page" in st.session_state and st.session_state.current_page in pages:
        default_index = pages.index(st.session_state.current_page)
    else:
        default_index = 0
    
    st.session_state.current_page = st.radio(
        "Select Workspace",
        pages,
        index=default_index,
        key="main_nav_radio",
        label_visibility="collapsed"
    )
    
    st.divider()

    # プロジェクト状況のタイトル
    st.markdown('<div class="section-header">Current Pipeline Status</div>', unsafe_allow_html=True)
    
    # 後程、非同期っぽく更新するためのプレースホルダー
    status_placeholder = st.empty()

    # デバッグ情報 (開発中のみ)
    with st.expander("🛠️ Debug Internals", expanded=False):
        st.write(f"Current Tab: {st.session_state.get('active_tab')}")
        st.write(f"Selected Title: {st.session_state.get('selected_title')}")
        st.write(f"Auto Script: {st.session_state.get('auto_script')}")
    
    # 自動保存設定
    st.markdown('<div class="section-header">Auto-Save Settings</div>', unsafe_allow_html=True)
    st.session_state.auto_save_enabled = st.checkbox(
        "生成時に自動保存",
        value=st.session_state.get("auto_save_enabled", True),
        help="Mode Bで台本生成が完了した際、自動的にドラフトとして保存します"
    )

# メインコンテンツエリア
if st.session_state.current_page == "Production Console":
    # セッション状態の初期化
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0
    
    # 自動保存設定の初期化
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True  # デフォルトで有効
    if "last_auto_save" not in st.session_state:
        st.session_state.last_auto_save = None
    if "auto_save_interval" not in st.session_state:
        st.session_state.auto_save_interval = 60  # 60秒ごと

    st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > Automated Content Pipeline</p>', unsafe_allow_html=True)

    # 進行状況インジケーター (Streamlit Native)
    steps = [
        {"icon": "✨", "label": "企画立案", "key": "ideation"},
        {"icon": "🖋️", "label": "台本作成", "key": "scripting"},
        {"icon": "🚀", "label": "制作実行", "key": "production"}
    ]
    
    # 外部からのタブ遷移指示がある場合の処理
    if st.session_state.get("next_step"):
        st.session_state.active_tab = st.session_state.next_step
        del st.session_state["next_step"]

    # プログレスバー型UIの描画（Streamlit Native）
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            # ステータスの判定
            if i < st.session_state.active_tab:
                # 完了
                status_color = "#0f172a"
                icon_display = "✓"
                label_color = "#64748b"
            elif i == st.session_state.active_tab:
                # 進行中
                status_color = "#3b82f6"
                icon_display = step["icon"]
                label_color = "#0f172a"
            else:
                # 未着手
                status_color = "#e2e8f0"
                icon_display = step["icon"]
                label_color = "#94a3b8"
            
            # ステップの描画
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <div style="
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    background: {status_color};
                    color: white;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    margin-bottom: 0.5rem;
                    border: 3px solid {status_color};
                ">
                    {icon_display}
                </div>
                <div style="
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: {label_color};
                ">
                    {step["label"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # Mode A: Ideation & Selection
    # ---------------------------------------------------------
    if st.session_state.active_tab == 0:
        st.markdown('### 📝 Mode A: Ideation')
        st.markdown('<p style="color: #94a3b8; font-size: 0.95rem;">マーケット分析に基づき、バズるネタを5つ提案します。採用するものを1つ選んでください。</p>', unsafe_allow_html=True)
        
        if st.button("Generate New Concepts", use_container_width=True):
            status_box = st.status("🎬 企画会議を開始します...", expanded=True)
            with status_box:
                try:
                    st.write("👥 エキスパートを召喚中...")
                    handler = SheetsHandler()
                    existing = handler.get_all_titles()
                    
                    st.write("📊 トレンドと既存コンテンツを分析中...")
                    ai = AIGenerator(model_name=st.session_state.selected_model)
                    
                    st.write("💡 新しい概念を鍛造（フォージ）中...")
                    ideas_data, full_response = ai.generate_new_ideas(existing, expert_persona=get_persona_str())
                    
                    st.session_state.new_ideas = list(ideas_data.keys())
                    st.session_state.all_ideas_data = ideas_data
                    st.session_state.ideation_full = full_response
                    st.session_state.trigger_forge_anim = True
                    
                    status_box.update(label="✅ 戦略立案が完了しました", state="complete", expanded=False)
                    st.toast("✨ 5つの新しい概念が鍛造されました", icon="🔥")
                except Exception as e:
                    status_box.update(label="❌ エラーが発生しました", state="error")
                    st.error(f"Error: {e}")

        # アニメーション用のクラス適用（セッション状態で制御）
        anim_class = "forge-animation" if st.session_state.get("trigger_forge_anim") else ""
        if st.session_state.get("trigger_forge_anim"):
            del st.session_state["trigger_forge_anim"] # 一回限り

        if "new_ideas" in st.session_state:
            with st.expander("📝 View AI Analysis & Discussion", expanded=False):
                st.markdown(st.session_state.ideation_full)
            
            st.markdown('<p style="font-size: 0.9rem; font-weight: 700;">制作に進めるネタを1つ選択してください：</p>', unsafe_allow_html=True)
            selected_idea = st.radio("Select Idea", st.session_state.new_ideas, label_visibility="collapsed")
            
            # --- New Input Fields for Script Context ---
            st.markdown("---")
            st.markdown("#### 🎬 台本の詳細設定 (任意)")
            st.info("アイディアに基づいて、より具体的な要望がある場合は入力してください。")
            
            user_title = st.text_input("タイトル (Title)", placeholder="例: 深夜の鏡の儀式", help="動画のメインテーマや仮のタイトルを指定します")
            user_hook = st.text_area("フック (Hook)", placeholder="例: 鏡に映った自分が瞬きをしない...", help="冒頭で視聴者を惹きつけるための要素を指定します")
            user_outline = st.text_area("アウトライン (Outline)", placeholder="例: 1.儀式の説明、2.異変の発生、3.衝撃の結末...", help="動画の構成や具体的な展開を指定します")

            if st.button("この情報で台本を作成する", use_container_width=True, type="primary"):
                st.session_state.selected_title = selected_idea
                st.session_state.selected_metadata = st.session_state.all_ideas_data.get(selected_idea, {})
                
                # ユーザー入力を保存
                st.session_state.user_script_context = {
                    "title": user_title,
                    "hook": user_hook,
                    "outline": user_outline
                }
                
                # 自動的にスクリプト生成フラグを立てて、タブを移動
                st.session_state.auto_script = True
                st.session_state.active_tab = 1 # Scriptingへ移動
                st.rerun()
                

    # ---------------------------------------------------------
    # Mode B: Scripting & Editorial
    # ---------------------------------------------------------
    elif st.session_state.active_tab == 1:
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown('### 🎬 Mode B: Scripting')
        with col_header2:
            if st.button("🔄 企画立案に戻る", use_container_width=True, help="現在の作業を破棄して、最初から企画を立て直します"):
                # リセット対象の変数リスト
                keys_to_reset = [
                    "new_ideas", "all_ideas_data", "ideation_full", "trigger_forge_anim",
                    "selected_title", "selected_metadata", "title_en", "title_jp",
                    "description", "hashtags", "editorial_notes", "current_script",
                    "script_jp_list", "mj_prompts_list", "auto_script"
                ]
                for key in keys_to_reset:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.active_tab = 0
                st.rerun()
        
        # Mode Aからの遷移、または直接開始
        target_title = st.session_state.get("selected_title")
        
        if target_title:
            st.success(f"Selected: **{target_title}**")
            
            # 自動生成フラグがある場合のみ実行
            if st.session_state.get("auto_script"):
                with st.status("🖋️ 台本作成中...", expanded=True):
                    try:
                        ai = AIGenerator(model_name=st.session_state.selected_model)
                        
                        # アイディアのメタデータとユーザー入力のコンテキストを統合
                        full_context = st.session_state.get("selected_metadata", {}).copy()
                        if "user_script_context" in st.session_state:
                            full_context.update(st.session_state.user_script_context)

                        res = ai.generate_script_and_prompts(
                            target_title, 
                            context=full_context,
                            expert_persona=get_persona_str()
                        )
                        # 新しい構造でセッションに保存
                        st.session_state.title_en = res.get("title_en", "")
                        st.session_state.title_jp = res.get("title_jp", "")
                        st.session_state.description = res.get("description", "")
                        st.session_state.hashtags = res.get("hashtags", "")
                        st.session_state.editorial_notes = res.get("editorial_notes", "")
                        st.session_state.current_script = res.get("vrew_script", "")
                        st.session_state.script_jp_list = res.get("script_jp_list", [])
                        st.session_state.mj_prompts_list = res.get("mj_prompts_list", [])
                        st.session_state.auto_script = False # 実行完了

                        # 【新規追加】生成完了直後の自動保存
                        if st.session_state.get("auto_save_enabled"):
                            try:
                                draft_mgr = DraftManager()
                                draft_data = {
                                    "selected_title": st.session_state.get("selected_title", ""),
                                    "selected_metadata": st.session_state.get("selected_metadata", {}),
                                    "title_en": st.session_state.get("title_en", ""),
                                    "title_jp": st.session_state.get("title_jp", ""),
                                    "description": st.session_state.get("description", ""),
                                    "hashtags": st.session_state.get("hashtags", ""),
                                    "editorial_notes": st.session_state.get("editorial_notes", ""),
                                    "vrew_script": st.session_state.get("current_script", ""),
                                    "script_jp_list": st.session_state.get("script_jp_list", []),
                                    "mj_prompts_list": st.session_state.get("mj_prompts_list", [])
                                }
                                from datetime import datetime
                                auto_draft_name = f"[自動保存] {st.session_state.get('selected_title', '無題')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                draft_mgr.save_draft(
                                    data=draft_data,
                                    draft_name=auto_draft_name,
                                    tags=["自動保存"],
                                    memo="生成完了時に自動保存されました"
                                )
                                st.toast("💾 生成完了にともない自動保存しました", icon="✅")
                            except Exception as e:
                                import logging
                                logging.error(f"Post-generation auto-save error: {e}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # 自動保存機能 (定期実行は廃止)
        pass

        # JavaScriptベースのコピーボタンを表示するヘルパー関数
        def display_with_copy(label, content, height=100, key_suffix="", help_text="", mid_content=""):
            import streamlit.components.v1 as components
            
            # テキストエリアを表示
            displayed_content = st.text_area(
                label, 
                value=content, 
                height=height, 
                key=f"area_{key_suffix}",
                label_visibility="visible"
            )
            
            # 日本語説明がある場合は表示
            if help_text:
                st.caption(help_text)

            # 中間に表示するコンテンツ（翻訳など）があれば表示
            if mid_content:
                st.markdown(mid_content, unsafe_allow_html=True)
            
            # JavaScriptによるコピー機能（リロードが発生しない）
            # content内のバックスラッシュやバッククォートをエスケープ
            escaped_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            
            html_code = f"""
                <button id="copy-btn-{key_suffix}" style="
                    width: 100%;
                    background-color: #0e1117;
                    color: white;
                    border: 1px solid rgba(250, 250, 250, 0.2);
                    padding: 0.6rem;
                    border-radius: 0.5rem;
                    cursor: pointer;
                    font-size: 0.9rem;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                ">📋 {label}をコピー</button>
                
                <script>
                    document.getElementById('copy-btn-{key_suffix}').onclick = function() {{
                        const text = `{escaped_content}`;
                        navigator.clipboard.writeText(text).then(() => {{
                            const btn = document.getElementById('copy-btn-{key_suffix}');
                            const oldText = btn.innerHTML;
                            btn.innerHTML = '✅ コピー完了！';
                            btn.style.backgroundColor = '#1e293b';
                            btn.style.borderColor = '#3b82f6';
                            setTimeout(() => {{
                                btn.innerHTML = oldText;
                                btn.style.backgroundColor = '#0e1117';
                                btn.style.borderColor = 'rgba(250, 250, 250, 0.2)';
                            }}, 2000);
                        }}).catch(err => {{
                            alert('コピーに失敗しました: ' + err);
                        }});
                    }};
                </script>
            """
            components.html(html_code, height=55)
            
            return displayed_content

        if "current_script" in st.session_state:
            # エディトリアルノート
            with st.expander("📝 View AI Production Notes", expanded=False):
                st.markdown(st.session_state.get("editorial_notes", ""))
            
            st.markdown("---")
            
            # タイトルセクション
            st.markdown("### 📝 タイトル")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">動画のタイトルを英語と日本語で編集できます。</p>', unsafe_allow_html=True)
            
            st.session_state.title_en = display_with_copy(
                "Title (EN)", 
                st.session_state.get("title_en", ""), 
                height=80,
                key_suffix="title_en",
                help_text="英語タイトル - YouTubeのタイトルとして使用されます"
            )
            
            st.session_state.title_jp = display_with_copy(
                "Title (JP)", 
                st.session_state.get("title_jp", ""), 
                height=80,
                key_suffix="title_jp",
                help_text="日本語タイトル - サムネイルや補足情報として使用されます"
            )
            
            st.markdown("---")
            
            # 説明文セクション
            st.markdown("### 📄 YouTube Description")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">動画の説明文を編集できます。</p>', unsafe_allow_html=True)
            
            st.session_state.description = display_with_copy(
                "Description", 
                st.session_state.get("description", ""), 
                height=150,
                key_suffix="description",
                help_text="動画説明文 - YouTubeの概要欄に表示されます"
            )
            
            st.markdown("---")
            
            # ハッシュタグセクション
            st.markdown("### #️⃣ Hashtags")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">動画に付けるハッシュタグを編集できます。</p>', unsafe_allow_html=True)
            
            st.session_state.hashtags = display_with_copy(
                "Hashtags", 
                st.session_state.get("hashtags", ""), 
                height=60,
                key_suffix="hashtags",
                help_text="ハッシュタグ - 動画の発見性を高めるために使用されます"
            )
            
            st.markdown("---")
            
            # 台本セクション
            st.markdown("### 📜 Vrew Script")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">Vrewで使用する台本を編集できます。</p>', unsafe_allow_html=True)
            
            st.session_state.current_script = display_with_copy(
                "Script (EN)", 
                st.session_state.get("current_script", ""), 
                height=300,
                key_suffix="vrew_script",
                help_text="英語台本 - Vrewにインポートして音声生成に使用されます"
            )
            
            st.markdown("---")
            
            # Midjourneyプロンプトセクション（シーン別）
            st.markdown("### 🎨 Midjourney Prompts")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">各シーンのMidjourneyプロンプトを編集できます。</p>', unsafe_allow_html=True)
            
            mj_list = st.session_state.get("mj_prompts_list", [])
            script_jp_list = st.session_state.get("script_jp_list", [])
            vrew_script = st.session_state.get("current_script", "").split("\n") if st.session_state.get("current_script") else []
            
            # --- オンデマンド翻訳ロジック ---
            # シーン数に対して翻訳が足りない場合の補完
            if vrew_script and len(script_jp_list) < len(vrew_script):
                with st.spinner("未翻訳のシーンをDeepLで翻訳中..."):
                    try:
                        from src.deepl_translator import DeepLTranslator
                        translator = DeepLTranslator()
                        # 足りない分だけ翻訳
                        for i in range(len(script_jp_list), len(vrew_script)):
                            line = vrew_script[i].strip()
                            if line:
                                script_jp_list.append(translator.translate(line))
                            else:
                                script_jp_list.append("")
                        st.session_state.script_jp_list = script_jp_list
                    except Exception as e:
                        st.error(f"オンデマンド翻訳エラー: {e}")

            if mj_list:
                for i, prompt in enumerate(mj_list, 1):
                    # 翻訳と原文のコンテンツを作成
                    mid_html = ""
                    if i <= len(script_jp_list):
                        ja_text = script_jp_list[i-1]
                        en_text = vrew_script[i-1] if i <= len(vrew_script) else ""
                        mid_html = f"""
                        <div style='margin-bottom: 0.8rem; font-size: 0.9rem;'>
                            <strong>シーン{i}の翻訳:</strong><br>
                            <span style='color: #0f172a;'>{ja_text}</span><br>
                            <span style='color: #64748b; font-style: italic;'>{en_text}</span>
                        </div>
                        """

                    updated_prompt = display_with_copy(
                        f"Scene {i}", 
                        prompt, 
                        height=120,
                        key_suffix=f"mj_scene_{i}",
                        help_text=f"シーン{i}の画像生成プロンプト - Midjourneyで使用されます",
                        mid_content=mid_html
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 更新された値をリストに反映
                    mj_list[i-1] = updated_prompt
                st.session_state.mj_prompts_list = mj_list
            else:
                st.info("Midjourneyプロンプトが生成されていません。")
            
            st.markdown("---")
            
            # ドラフト保存ボタン
            st.markdown("### 💾 Save Draft")
            st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">現在の作業内容をドラフトとして保存できます。</p>', unsafe_allow_html=True)
            
            col_save1, col_save2 = st.columns([2, 1])
            with col_save1:
                draft_name_input = st.text_input("ドラフト名", placeholder="例: ホラー台本 v1", key="draft_name_input")
            with col_save2:
                draft_tags_input = st.text_input("タグ (カンマ区切り)", placeholder="例: ホラー,実験的", key="draft_tags_input")
            
            draft_memo_input = st.text_area("メモ (オプション)", placeholder="このドラフトについてのメモ...", height=80, key="draft_memo_input")
            
            if st.button("💾 Save as Draft", key="save_draft_btn", use_container_width=True):
                if not draft_name_input:
                    st.warning("ドラフト名を入力してください。")
                else:
                    try:
                        draft_mgr = DraftManager()
                        
                        # 保存するデータを準備
                        draft_data = {
                            "selected_title": st.session_state.get("selected_title", ""),
                            "selected_metadata": st.session_state.get("selected_metadata", {}),
                            "title_en": st.session_state.get("title_en", ""),
                            "title_jp": st.session_state.get("title_jp", ""),
                            "description": st.session_state.get("description", ""),
                            "hashtags": st.session_state.get("hashtags", ""),
                            "editorial_notes": st.session_state.get("editorial_notes", ""),
                            "vrew_script": st.session_state.get("current_script", ""),
                            "script_jp_list": st.session_state.get("script_jp_list", []),
                            "mj_prompts_list": st.session_state.get("mj_prompts_list", [])
                        }
                        
                        # タグを処理
                        tags = [tag.strip() for tag in draft_tags_input.split(",") if tag.strip()] if draft_tags_input else []
                        
                        # 保存
                        draft_id = draft_mgr.save_draft(
                            data=draft_data,
                            draft_name=draft_name_input,
                            tags=tags,
                            memo=draft_memo_input
                        )
                        
                        st.success(f"✅ ドラフト '{draft_name_input}' を保存しました！")
                        st.toast("💾 ドラフトを保存しました", icon="✅")
                        
                    except Exception as e:
                        st.error(f"保存エラー: {e}")
            
            st.markdown("---")
            
            # 公開ボタン
            if st.button("Finalize & Publish to Production", key="publish_to_prod", use_container_width=True):
                with st.spinner("Publishing to Sheets..."):
                    try:
                        handler = SheetsHandler()
                        
                        # 重複チェック: A列（タイトル）をすべて取得
                        existing_titles = handler.get_all_titles()
                        
                        # 既にある場合は、新規追加（append）せずに、その行のインデックスを取得
                        if target_title in existing_titles:
                            # 1-indexed (Header is 1, data starts from 2)
                            new_row_idx = existing_titles.index(target_title) + 2
                            st.info(f"Existing title found at row {new_row_idx}. Updating existing record.")
                        else:
                            # A列に新しい行として追加し、同時にB,C列を書き込む
                            handler.append_new_titles([target_title])
                            # 今追加した行のインデックスを取得（最後尾）
                            all_titles_after = handler.worksheet.col_values(1)
                            new_row_idx = len(all_titles_after)
                        
                        # プロンプトを連結して保存
                        combined_prompts = "\n\n".join(st.session_state.mj_prompts_list)
                        handler.update_row_data(new_row_idx, st.session_state.current_script, combined_prompts)
                        
                        st.success("Published! Moving to Production...")
                        # データをクリアしてMode Cへ移動
                        st.session_state.production_ready = True
                        st.session_state.prod_title = target_title
                        st.session_state.prod_script = st.session_state.current_script
                        st.session_state.prod_prompt = combined_prompts
                        st.session_state.prod_row = new_row_idx
                        
                        # セッション状態のリセット
                        if "selected_title" in st.session_state:
                            del st.session_state.selected_title
                        if "current_script" in st.session_state:
                            del st.session_state.current_script
                        
                        # ナビゲーション指示
                        st.session_state.tab_to_redirect = 2 # Productionへ移動
                        st.session_state.page_to_redirect = "Production Console"
                        
                    except Exception as e:
                        st.error(f"Publish failed: {e}")
                        st.stop() # ここで停止して表示を維持

                # st.rerun() は try/except の外で行う (RerunException回避のため)
                st.rerun()

        else:
            st.warning("Please select an idea in Mode A first.")
            

    # ---------------------------------------------------------
    # Mode C: Asset Production
    # ---------------------------------------------------------
    elif st.session_state.active_tab == 2:
        col_c_header1, col_c_header2 = st.columns([3, 1])
        with col_c_header1:
            st.markdown('### 📽️ Mode C: Asset Production')
        with col_c_header2:
            if st.button("🔄 企画立案に戻る", key="reset_from_c", use_container_width=True, help="制作を中止して、最初から企画を立て直します"):
                keys_to_reset = [
                    "new_ideas", "all_ideas_data", "ideation_full", "trigger_forge_anim",
                    "selected_title", "selected_metadata", "title_en", "title_jp",
                    "description", "hashtags", "editorial_notes", "current_script",
                    "script_jp_list", "mj_prompts_list", "auto_script",
                    "production_ready", "prod_title", "prod_script", "prod_prompt", "prod_row", "production_status", "launch_log"
                ]
                for key in keys_to_reset:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.active_tab = 0
                st.rerun()

        # 認証管理セクション
        with st.expander("🔐 Authentication & Session Management", expanded=False):
            st.info("初回またはログインが切れた場合は、以下のボタンからログインしてブラウザを閉じてください。セッションが保存されます。")
            c_auth1, c_auth2 = st.columns(2)
            from src.auth_manager import AuthManager
            
            with c_auth1:
                if st.button("🔑 Login to Midjourney", use_container_width=True):
                    with st.spinner("Launching login browser..."):
                        AuthManager.save_session("https://www.midjourney.com/explore")
                    st.success("Midjourney session update process finished.")
            
            with c_auth2:
                if st.button("🔑 Login to Vrew", use_container_width=True):
                    with st.spinner("Launching login browser..."):
                        AuthManager.save_session("https://vrew.voyagerx.com/ja/")
                    st.success("Vrew session update process finished.")
        
        st.divider()
        if st.session_state.get("production_ready"):
            st.success(f"🔥 Currently Producing: **{st.session_state.prod_title}**")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.expander("📖 Operation Guide", expanded=True):
                    st.markdown("""
                    <div style="font-size: 0.9rem; color: #1e293b; background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                        1. <b>Launch Production Engines</b> ボタンを押すと <b>Midjourney</b> と <b>Vrew</b> が並列で起動します。<br>
                        2. <b>Midjourney</b>: プロンプトが入力されています。Enterで生成を開始。<br>
                        3. <b>Vrew</b>: 台本がインポートされています。AIボイス・BGMを設定して書き出し。<br>
                        4. 完了後、<b>Finish & Mark as Complete</b> を押してシートに記録します。
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # 制作状況パネル
                st.markdown('<div class="section-header">Live Status</div>', unsafe_allow_html=True)
                if "production_status" not in st.session_state:
                    st.session_state.production_status = "Waiting to Launch"
                
                status_color = "#3b82f6" if st.session_state.production_status != "Completed" else "#10b981"
                st.markdown(f"""
                <div style="padding: 1rem; background: #f1f5f9; border-radius: 12px; border-left: 5px solid {status_color};">
                    <span style="font-size: 0.8rem; font-weight: 800; color: #64748b; text-transform: uppercase;">Current State</span><br>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">{st.session_state.production_status}</span>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # 制作エンジン設定
            st.markdown('<div class="section-header">Engine Settings</div>', unsafe_allow_html=True)
            c_set1, c_set2 = st.columns(2)
            with c_set1:
                vrew_style = st.text_input("🎨 Vrew Video Style", value="情報の伝達", help="Vrewのスタイル選択画面に表示される名前を入力してください。")
            with c_set2:
                vrew_ratio = st.selectbox("📐 Aspect Ratio", ["16:9", "9:16", "1:1", "4:5"], index=0)

            # 起動ステータスの管理
            if "launch_log" not in st.session_state:
                st.session_state.launch_log = []

            if st.button("🚀 Launch Production Engines", use_container_width=True, type="primary"):
                try:
                    import subprocess
                    import sys
                    import os
                    
                    root_dir = os.path.abspath(os.getcwd())
                    helper_path = os.path.join(root_dir, "src", "automation_helper.py")
                    temp_dir = os.path.join(root_dir, "data", "temp_exec")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    st.session_state.launch_log = ["🕒 起動プロセスを開始しました..."]
                    
                    # 一時ファイル書き出し
                    prompt_path = os.path.join(temp_dir, "prompt.txt")
                    script_path = os.path.join(temp_dir, "script.txt")
                    with open(prompt_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state.prod_prompt)
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state.prod_script)
                    
                    env = os.environ.copy()
                    env["PYTHONPATH"] = root_dir + os.pathsep + env.get("PYTHONPATH", "")
                    cflags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                    
                    # 起動実行
                    st.session_state.launch_log.append("🎬 Midjourney エンジンを起動中...")
                    subprocess.Popen([sys.executable, helper_path, "mj", prompt_path], env=env, cwd=root_dir, creationflags=cflags)
                    
                    st.session_state.launch_log.append(f"🎬 Vrew エンジンを起動中... (Style: {vrew_style}, Ratio: {vrew_ratio})")
                    subprocess.Popen([sys.executable, helper_path, "vrew", script_path, vrew_style, vrew_ratio], env=env, cwd=root_dir, creationflags=cflags)
                    
                    st.session_state.production_status = "Engines Running (Active)"
                    st.session_state.launch_log.append("✅ すべてのエンジンを起動しました。")
                    st.toast("Production engines launched!", icon="🚀")
                    st.rerun()

                except Exception as e:
                    st.error(f"Launch Error: {e}")
                    st.session_state.launch_log.append(f"🚨 エラー: {e}")

            # 実行ログと手動コマンド (トラブル時に備えて保持)
            if st.session_state.launch_log:
                with st.expander("🛠️ View Execution Details / Manual Command", expanded=False):
                    for log_item in st.session_state.launch_log:
                        st.write(log_item)
                    
                    st.markdown("---")
                    st.caption("Manual Override (PowerShell):")
                    root_dir = os.path.abspath(os.getcwd())
                    vrew_cmd = f"& '{sys.executable}' '{os.path.join(root_dir, 'src', 'automation_helper.py')}' vrew '{os.path.join(root_dir, 'data', 'temp_exec', 'script.txt')}' '{vrew_style}' '{vrew_ratio}'"
                    st.code(f"& '{sys.executable}' '{os.path.join(root_dir, 'src', 'automation_helper.py')}' mj '{os.path.join(root_dir, 'data', 'temp_exec', 'prompt.txt')}'")
                    st.code(vrew_cmd)
            # --------------------------------------------------------

            if st.button("✅ Finish & Mark as Complete", key="mark_final", use_container_width=True):
                with st.spinner("シートを更新中..."):
                    try:
                        handler = SheetsHandler()
                        handler.mark_as_completed(st.session_state.prod_row)
                        st.snow()
                        st.toast(f"Completed: {st.session_state.prod_title}", icon="🎊")
                        
                        # 制作データのクリア
                        del st.session_state.production_ready
                        if "production_status" in st.session_state:
                            del st.session_state.production_status
                        
                        # キューが空になった場合を想定し、タブを戻さずそのままにするか、最初に戻す
                        st.success("Project marked as complete!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sheets Update Error: {e}")

        else:
            # 制作対象がない場合
            st.info("制作キューが空です。Googleスプレッドシートから未処理の台本を読み込みます。")
            
            if st.button("📥 Load Next from Sheets Queue", use_container_width=True):
                with st.spinner("Fetching data from Google Sheets..."):
                    try:
                        handler = SheetsHandler()
                        row_idx, row_data = handler.get_unprocessed_row()
                        if row_idx and len(row_data) >= 3:
                            st.session_state.production_ready = True
                            st.session_state.prod_title = row_data[0]
                            st.session_state.prod_script = row_data[1]
                            st.session_state.prod_prompt = row_data[2]
                            st.session_state.prod_row = row_idx
                            st.session_state.production_status = "Ready to Launch"
                            st.rerun()
                        else:
                            st.warning("シートに未処理の台本が見つかりませんでした。")
                    except Exception as e:
                        st.error(f"Queue Loading Error: {e}")


elif st.session_state.current_page == "📋 Draft List":
    st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > Draft List</p>', unsafe_allow_html=True)
    
    st.markdown('### 📋 Draft List')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 2rem;">保存済みのドラフトを一覧表示・管理します。</p>', unsafe_allow_html=True)
    
    try:
        draft_mgr = DraftManager()
        
        # ページネーション用のセッション状態を初期化
        if "draft_list_page_size" not in st.session_state:
            st.session_state.draft_list_page_size = 20  # 一覧ページでは20件ずつ
        if "draft_list_offset" not in st.session_state:
            st.session_state.draft_list_offset = 0
        
        # 総数を取得
        total_count = draft_mgr.count_drafts()
        
        # ページネーションでドラフトを取得
        drafts = draft_mgr.list_drafts(
            limit=st.session_state.draft_list_page_size,
            offset=st.session_state.draft_list_offset
        )
        
        if total_count > 0:
            # ヘッダー情報
            showing_from = st.session_state.draft_list_offset + 1
            showing_to = min(st.session_state.draft_list_offset + len(drafts), total_count)
            st.markdown(f"**{showing_from}-{showing_to}件を表示中 (全{total_count}件)**")
            st.markdown("---")
            
            for draft in drafts:
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {draft['draft_name']}")
                        if draft.get('title_en'):
                            st.markdown(f"**EN:** {draft['title_en']}")
                        if draft.get('title_jp'):
                            st.markdown(f"**JP:** {draft['title_jp']}")
                        if draft.get('tags'):
                            tags_display = " ".join([f"`{tag}`" for tag in draft['tags']])
                            st.markdown(f"**Tags:** {tags_display}")
                        st.caption(f"📅 保存日時: {draft['created_at'][:19].replace('T', ' ')}")
                        if draft.get('memo'):
                            with st.expander("📝 メモを表示"):
                                st.write(draft['memo'])
                    
                    with col2:
                        if st.button("🔄 復元", key=f"restore_{draft['id']}", use_container_width=True):
                            loaded = draft_mgr.load_draft(draft['id'])
                            if loaded:
                                data = loaded.get('data', {})
                                # セッション状態を更新
                                st.session_state.selected_title = data.get('selected_title', '')
                                st.session_state.selected_metadata = data.get('selected_metadata', {})
                                st.session_state.title_en = data.get('title_en', '')
                                st.session_state.title_jp = data.get('title_jp', '')
                                st.session_state.description = data.get('description', '')
                                st.session_state.hashtags = data.get('hashtags', '')
                                st.session_state.editorial_notes = data.get('editorial_notes', '')
                                st.session_state.current_script = data.get('vrew_script', '')
                                st.session_state.mj_prompts_list = data.get('mj_prompts_list', [])
                                
                                # ページ遷移の指示
                                st.session_state.tab_to_redirect = 1  # Mode Bへ
                                st.session_state.page_to_redirect = "Production Console"
                                
                                st.toast(f"✅ ドラフト '{draft['draft_name']}' を復元しました", icon="🔄")
                                st.rerun()
                    
                    with col3:
                        if st.button("🗑️ 削除", key=f"delete_{draft['id']}", use_container_width=True):
                            if draft_mgr.delete_draft(draft['id']):
                                st.toast(f"🗑️ ドラフト '{draft['draft_name']}' を削除しました", icon="✅")
                                st.rerun()
                    
                    st.markdown("---")
            
            # ページネーションコントロール
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            
            with col_prev:
                if st.session_state.draft_list_offset > 0:
                    if st.button("⬅️ 前のページ", key="prev_page_list", use_container_width=True):
                        st.session_state.draft_list_offset = max(0, st.session_state.draft_list_offset - st.session_state.draft_list_page_size)
                        st.rerun()
            
            with col_info:
                current_page = (st.session_state.draft_list_offset // st.session_state.draft_list_page_size) + 1
                total_pages = (total_count + st.session_state.draft_list_page_size - 1) // st.session_state.draft_list_page_size
                st.markdown(f"<p style='text-align: center; font-weight: 600;'>ページ {current_page} / {total_pages}</p>", unsafe_allow_html=True)
            
            with col_next:
                if showing_to < total_count:
                    if st.button("次のページ ➡️", key="next_page_list", use_container_width=True):
                        st.session_state.draft_list_offset += st.session_state.draft_list_page_size
                        st.rerun()
        else:
            st.info("📭 保存済みドラフトはありません。")
            st.markdown("Production Console > Mode Bで台本を作成し、ドラフトとして保存してください。")
            
    except Exception as e:
        st.error(f"ドラフトの読み込みエラー: {e}")


elif st.session_state.current_page == "🎭 AI Persona Studio":
    st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > AI Persona Studio</p>', unsafe_allow_html=True)
    
    st.markdown('### 🎭 AI Persona Studio')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 2rem;">エージェントの性格と専門知識をカスタマイズします。ここでの設定は、台本生成時の「論議」と「成果物」の品質に直結します。</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-header">📈 Viral Architect</div>', unsafe_allow_html=True)
        st.session_state.persona_prompts["marketer"] = st.text_area(
            "Marketer Persona", 
            st.session_state.persona_prompts["marketer"], 
            height=300,
            key="ma_area",
            label_visibility="collapsed"
        )
        st.caption("YouTube Shortsのトレンド分析とフック担当")
        
    with col2:
        st.markdown('<div class="section-header">✍️ The Whisperer</div>', unsafe_allow_html=True)
        st.session_state.persona_prompts["writer"] = st.text_area(
            "Writer Persona", 
            st.session_state.persona_prompts["writer"], 
            height=300,
            key="tw_area",
            label_visibility="collapsed"
        )
        st.caption("Jホラーの不気味さと台本構成担当")
        
    with col3:
        st.markdown('<div class="section-header">🎥 The Visionary</div>', unsafe_allow_html=True)
        st.session_state.persona_prompts["director"] = st.text_area(
            "Director Persona", 
            st.session_state.persona_prompts["director"], 
            height=300,
            key="vi_area",
            label_visibility="collapsed"
        )
        st.caption("Midjourneyの映像演出とプロンプト担当")
    
    st.divider()
    
    c_btn1, c_btn2, _ = st.columns([1, 1, 2])
    with c_btn1:
        if st.button("Save & Apply Changes", use_container_width=True):
            st.success("Personas updated successfully.")
    with c_btn2:
        if st.button("Reset to Default", use_container_width=True):
            st.session_state.persona_prompts = DEFAULT_PERSONAS.copy()
            st.rerun()
            

elif st.session_state.current_page == "⚙️ System Configuration":
    st.markdown('<p style="font-size: 0.8rem; color: #64748b; margin-bottom: 2rem;">Production Hub > System Configuration</p>', unsafe_allow_html=True)
    
    st.markdown('### ⚙️ System Configuration')
    st.markdown('<p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 2rem;">システムのコア設定を管理します。APIキーの変更や外部サービスとの認証を行います。</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Gemini API Connection</div>', unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", value=Config.GEMINI_API_KEY or "", type="password")
    if st.button("Update API Key", use_container_width=True):
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
        st.success("API Key updated and saved to .env file.")
            
    st.divider()

    st.markdown('<div class="section-header">AI Content Engine</div>', unsafe_allow_html=True)
    st.session_state.selected_model = st.selectbox(
        "AI Generation Model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"],
        index=2 if st.session_state.selected_model == "gemini-3-flash-preview" else (1 if st.session_state.selected_model == "gemini-2.5-pro" else 0),
        help="生成に使用するGeminiモデルを選択します。gemini-3-flash-previewが最新のプレビューモデルです。"
    )
    
    st.divider()

    st.markdown('<div class="section-header">External Auth Sessions</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">自動化エンジンのセッションを保存します。</p>', unsafe_allow_html=True)
    
    col_mj_btn, col_vr_btn, _ = st.columns([1, 1, 2])
    with col_mj_btn:
        if st.button("Launch MJ Auth", use_container_width=True):
            AuthManager.save_session("https://www.midjourney.com/explore")
            st.info("Midjourney auth session initiated.")
    with col_vr_btn:
        if st.button("Launch Vrew Auth", use_container_width=True):
            AuthManager.save_session("https://vrew.voyagerx.com/ja/")
            st.info("Vrew auth session initiated.")
            

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
