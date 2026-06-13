import streamlit as st
import uuid
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from utils.core_logic import build_novel_chain, start_new_game, NOVEL_WORLDS
from utils import db_manager

db_manager.init_db()

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&family=Playfair+Display:wght@700&family=Ma+Shan+Zheng&family=ZCOOL+KuaiLe&display=swap');

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --secondary: #a855f7;
    --accent: #ec4899;
    --accent-light: #f472b6;
    --bg-dark: #0c0a1a;
    --bg-card: #16132e;
    --bg-card-hover: #1e1a3d;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: rgba(139, 92, 246, 0.15);
    --border-glow: rgba(139, 92, 246, 0.4);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
    --shadow-md: 0 8px 32px rgba(0,0,0,0.4);
    --shadow-lg: 0 16px 64px rgba(0,0,0,0.5);
    --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --gradient-card: linear-gradient(145deg, rgba(99,102,241,0.08), rgba(168,85,247,0.08));
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg-dark) !important;
    background-image: 
        radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, rgba(236,72,153,0.04) 0%, transparent 50%) !important;
    min-height: 100vh;
}

.main .block-container {
    padding-top: 1rem;
    max-width: 1100px;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12102a 0%, #0c0a1a 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div {
    padding-top: 0.5rem;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Sans SC', sans-serif !important;
}

.hero-title {
    font-family: 'Playfair Display', 'Noto Sans SC', serif;
    font-size: 2.8rem;
    font-weight: 900;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin: 0;
    line-height: 1.3;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 300;
    letter-spacing: 0.05em;
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25) !important;
    letter-spacing: 0.02em;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s ease;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99, 102, 241, 0.4) !important;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2) !important;
}

[data-testid="stChatMessage"] {
    background: var(--gradient-card) !important;
    border-radius: 18px !important;
    padding: 1.2rem 1.4rem !important;
    margin: 0.6rem 0 !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: blur(12px);
    animation: messageSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    transition: border-color 0.3s ease;
}

[data-testid="stChatMessage"]:hover {
    border-color: var(--border-glow);
}

@keyframes messageSlide {
    from { opacity: 0; transform: translateY(16px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.2); }
    50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.4); }
}

[data-testid="stSpinner"] > div {
    color: var(--primary-light) !important;
}

[data-testid="stChatInput"] {
    background: rgba(22, 19, 46, 0.95) !important;
    border-radius: 18px !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s ease;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
}

[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-size: 1rem !important;
}

[data-testid="stMetric"] {
    background: var(--gradient-card) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid var(--border) !important;
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    border-color: var(--border-glow);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}

.stDivider {
    border-color: var(--border) !important;
    opacity: 0.6;
}

.stInfo {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.1)) !important;
    border-left: 4px solid var(--primary) !important;
    border-radius: 0 12px 12px 0 !important;
}

.stMarkdown {
    color: var(--text-primary);
}

.stMarkdown p, .stMarkdown li {
    color: var(--text-secondary);
    line-height: 1.85;
}

.stCaption {
    color: var(--text-muted) !important;
}

.hero-section {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.08), rgba(236, 72, 153, 0.06));
    border-radius: 24px;
    padding: 3.5rem 2.5rem;
    text-align: center;
    border: 1px solid var(--border);
    margin: 1rem 0 2rem 0;
    backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.6s ease;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.03) 0%, transparent 60%);
    animation: float 8s ease-in-out infinite;
}

.sidebar-brand {
    text-align: center;
    padding: 1.8rem 1.2rem;
    background: linear-gradient(145deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.1));
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}

.sidebar-brand::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
    animation: shimmer 4s infinite;
}

.sidebar-brand h2 {
    margin: 0 !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-brand p {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin: 0.4rem 0 0 0;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.3rem 0.9rem;
    border-radius: 24px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

.status-online {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse-glow 2s infinite;
}

.world-card {
    background: var(--gradient-card);
    border-radius: 18px;
    padding: 1.8rem;
    border: 1px solid var(--border);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.world-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.25);
    border-color: var(--primary);
}

.world-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-hero);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.world-card:hover::before {
    opacity: 1;
}

.feature-item {
    background: var(--gradient-card);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    border: 1px solid var(--border);
    margin: 0.5rem 0;
    transition: all 0.3s ease;
}

.feature-item:hover {
    border-color: var(--border-glow);
    transform: translateX(4px);
}

.stat-card {
    background: var(--gradient-card);
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid var(--border);
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    border-color: var(--border-glow);
    box-shadow: var(--shadow-sm);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.inventory-tag {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.15));
    color: var(--primary-light);
    padding: 0.35rem 0.85rem;
    border-radius: 10px;
    font-size: 0.85rem;
    margin: 0.25rem;
    border: 1px solid rgba(99, 102, 241, 0.2);
    transition: all 0.2s ease;
}

.inventory-tag:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.25));
    transform: scale(1.02);
}

.clue-card {
    background: var(--gradient-card);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border);
    margin: 0.4rem 0;
    transition: all 0.3s ease;
}

.clue-card:hover {
    border-color: var(--accent);
}

.section-header {
    color: var(--text-primary);
    font-size: 0.95rem;
    font-weight: 600;
    margin: 1rem 0 0.6rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.divider-fancy {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
    border: none;
}

.empty-state {
    text-align: center;
    padding: 2.5rem;
    color: var(--text-muted);
}

.empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .hero-section { padding: 2rem 1.2rem; border-radius: 18px; }
    .main .block-container { padding: 0.8rem; }
    [data-testid="stChatMessage"] { padding: 1rem; border-radius: 14px; }
    .world-card { padding: 1.2rem; }
}

.animate-float { animation: float 4s ease-in-out infinite; }
.glow { text-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.5); }

.character-creator {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border);
    margin: 1rem 0;
    animation: fadeInUp 0.6s ease;
}

.class-card {
    background: var(--gradient-card);
    border-radius: 14px;
    padding: 1.2rem;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}

.class-card:hover {
    border-color: var(--primary);
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}

.save-slot {
    background: var(--gradient-card);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border);
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
}

.save-slot:hover {
    border-color: var(--primary);
    transform: translateX(4px);
}

.save-indicator {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 0.3rem 0.8rem;
    border-radius: 8px;
    font-size: 0.75rem;
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
}
</style>
"""

st.set_page_config(
    page_title="沉浸式多角色互动小说引擎",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "# 🎭 沉浸式多角色互动小说引擎\nAI驱动的沉浸式文字冒险游戏",
    },
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if st.session_state.theme in THEMES:
    t = THEMES[st.session_state.theme]
    st.markdown(f"""
    <style>
    :root {{
        --primary: {t['primary']};
        --secondary: {t['secondary']};
        --bg-dark: {t['bg']};
        --bg-card: {t['card']};
        --gradient-hero: {t['gradient']};
    }}
    .stApp {{ background: {t['bg']} !important; }}
    .sidebar-brand h2 {{ background: {t['gradient']}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero-title {{ background: {t['gradient']}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .stat-value {{ background: {t['gradient']}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .stButton > button {{ background: {t['gradient']} !important; }}
    </style>
    """, unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "novel_title" not in st.session_state:
    st.session_state.novel_title = None

if "game_chain" not in st.session_state:
    st.session_state.game_chain = None

if "theme" not in st.session_state:
    st.session_state.theme = "暗夜紫"

if "character_created" not in st.session_state:
    st.session_state.character_created = False

if "character_name" not in st.session_state:
    st.session_state.character_name = ""

if "character_class" not in st.session_state:
    st.session_state.character_class = ""

if "character_background" not in st.session_state:
    st.session_state.character_background = ""

THEMES = {
    "暗夜紫": {
        "primary": "#6366f1", "secondary": "#a855f7", "bg": "#0c0a1a",
        "card": "#16132e", "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
    },
    "烈焰红": {
        "primary": "#ef4444", "secondary": "#f97316", "bg": "#1a0a0a",
        "card": "#2e1616", "gradient": "linear-gradient(135deg, #ef4444 0%, #f97316 50%, #fbbf24 100%)"
    },
    "翡翠绿": {
        "primary": "#10b981", "secondary": "#06b6d4", "bg": "#0a1a14",
        "card": "#162e22", "gradient": "linear-gradient(135deg, #10b981 0%, #06b6d4 50%, #22d3ee 100%)"
    },
    "星辰蓝": {
        "primary": "#3b82f6", "secondary": "#8b5cf6", "bg": "#0a0f1a",
        "card": "#162030", "gradient": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #a855f7 100%)"
    },
    "樱花粉": {
        "primary": "#ec4899", "secondary": "#f472b6", "bg": "#1a0a14",
        "card": "#2e1624", "gradient": "linear-gradient(135deg, #ec4899 0%, #f472b6 50%, #fbbf24 100%)"
    },
}

CHARACTER_CLASSES = {
    "战士": {"icon": "⚔️", "hp": 120, "attack": 18, "defense": 15, "desc": "近战强者，擅长正面交锋"},
    "法师": {"icon": "🔮", "hp": 80, "attack": 22, "defense": 8, "desc": "掌控元素之力，擅长远程攻击"},
    "游侠": {"icon": "🏹", "hp": 90, "attack": 16, "defense": 12, "desc": "敏捷灵活，擅长侦查与暗杀"},
    "牧师": {"icon": "✝️", "hp": 100, "attack": 10, "defense": 14, "desc": "治愈大师，擅长辅助与治疗"},
}


def init_game(novel_title: str, char_name: str = "无名", char_class: str = "战士", char_background: str = ""):
    class_info = CHARACTER_CLASSES.get(char_class, CHARACTER_CLASSES["战士"])
    session_id = start_new_game(
        st.session_state.user_id, novel_title,
        char_name=char_name, char_class=char_class,
        hp=class_info["hp"], attack=class_info["attack"], defense=class_info["defense"]
    )
    st.session_state.session_id = session_id
    st.session_state.novel_title = novel_title
    st.session_state.messages = []
    st.session_state.game_chain = build_novel_chain(novel_title)
    st.session_state.character_created = True

    bg_text = f"\n\n**你的背景故事：**{char_background}" if char_background else ""

    intro_msg = (
        f"### 🌟 欢迎来到《{novel_title}》\n\n"
        f"你是一名 **{char_class}**，名为「{char_name}」。{class_info['desc']}。\n\n"
        "你睁开眼睛，发现自己置身于一个陌生的世界。空气中弥漫着未知的气息...\n\n"
        "---\n\n"
        f"**角色属性：** HP={class_info['hp']} | 攻击={class_info['attack']} | 防御={class_info['defense']}"
        f"{bg_text}\n\n"
        "**你可以自由行动：**\n\n"
        "| 指令 | 说明 |\n"
        "|------|------|\n"
        "| 🗺️ `探索` | 向前探索未知区域 |\n"
        "| 💬 `对话` | 寻找NPC进行对话 |\n"
        "| ⚔️ `战斗` | 寻找敌人进行战斗 |\n"
        "| 🔍 `查看线索` | 了解已收集的信息 |\n"
        "| 📊 `状态` | 查看角色属性 |\n"
        "| 💾 `存档` | 保存当前进度 |\n\n"
        "> 💡 *提示：你可以自由输入任何行动，AI会根据你的选择推进故事。*"
    )
    st.session_state.messages.append({"role": "assistant", "content": intro_msg})


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <h2>🎭 互动小说引擎</h2>
            <p>AI驱动 · 沉浸体验</p>
            <span class="status-badge status-online">
                <span class="status-dot"></span>
                在线运行
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">🎨 主题风格</div>', unsafe_allow_html=True)
    theme_names = list(THEMES.keys())
    cols = st.columns(5)
    for i, theme_name in enumerate(theme_names):
        with cols[i]:
            if st.button("●", key=f"theme_{theme_name}", help=theme_name,
                        type="primary" if st.session_state.theme == theme_name else "secondary"):
                st.session_state.theme = theme_name
                st.rerun()

    st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">🌍 选择世界</div>', unsafe_allow_html=True)
    for title, world_info in NOVEL_WORLDS.items():
        if st.button(f"📖 {title}", key=f"btn_{title}", use_container_width=True):
            st.session_state.novel_title = title
            st.session_state.character_created = False
            st.rerun()

    if st.session_state.novel_title and not st.session_state.character_created:
        st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">👤 创建角色</div>', unsafe_allow_html=True)

        char_name = st.text_input("角色名称", value="", placeholder="输入你的角色名")
        char_class = st.selectbox("选择职业", list(CHARACTER_CLASSES.keys()))
        char_background = st.text_area("背景故事（可选）", placeholder="描述你的角色背景...", height=80)

        if char_class:
            info = CHARACTER_CLASSES[char_class]
            st.markdown(
                f"""<div style="background:var(--gradient-card);border-radius:10px;padding:0.8rem;border:1px solid var(--border);margin-top:0.5rem">
                    <div style="font-size:1.5rem;text-align:center">{info['icon']}</div>
                    <div style="text-align:center;color:var(--text-secondary);font-size:0.85rem;margin-top:0.3rem">{info['desc']}</div>
                    <div style="text-align:center;color:var(--text-muted);font-size:0.75rem;margin-top:0.3rem">HP:{info['hp']} | ATK:{info['attack']} | DEF:{info['defense']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        if st.button("🎮 开始冒险", use_container_width=True, type="primary"):
            if not char_name:
                char_name = "无名"
            init_game(st.session_state.novel_title, char_name, char_class, char_background)
            st.rerun()

    st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)

    if st.session_state.session_id:
        session = db_manager.get_session(st.session_state.session_id)
        if session:
            st.markdown('<div class="section-header">📊 角色状态</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""<div class="stat-card">
                        <div class="stat-value">{session.get('hp', 100)}</div>
                        <div class="stat-label">❤️ 生命值</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""<div class="stat-card">
                        <div class="stat-value">Ch.{session.get('current_chapter', 1)}</div>
                        <div class="stat-label">📖 当前章节</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            atk = session.get('attack', 15)
            dfn = session.get('defense', 10)
            st.markdown(
                f"""<div class="stat-card" style="margin-top:0.5rem">
                    <div class="stat-value" style="font-size:1.3rem">{atk} / {dfn}</div>
                    <div class="stat-label">⚔️ 攻击 / 🛡️ 防御</div>
                </div>""",
                unsafe_allow_html=True,
            )

            inventory = session.get("inventory", [])
            if inventory:
                st.markdown('<div class="section-header">🎒 物品栏</div>', unsafe_allow_html=True)
                tags_html = "".join(
                    f'<span class="inventory-tag">{item}</span>' for item in inventory
                )
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px">{tags_html}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">📋 已收集线索</div>', unsafe_allow_html=True)
            clues = db_manager.get_clues(st.session_state.session_id)
            if clues:
                for c in clues:
                    with st.expander(f"[{c['clue_type']}] 线索"):
                        st.write(c['clue_content'][:150] + "..." if len(c['clue_content']) > 150 else c['clue_content'])
            else:
                st.markdown(
                    '<div class="empty-state"><div class="empty-state-icon">🔍</div><p>暂无线索</p></div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">💾 存档管理</div>', unsafe_allow_html=True)

            saves = db_manager.get_saves_for_session(st.session_state.session_id)
            if saves:
                for save in saves:
                    with st.expander(f"📁 {save['save_name']} ({save['created_at'][:10]})"):
                        if st.button("📥 加载此存档", key=f"load_{save['save_id']}", use_container_width=True):
                            db_manager.load_game_snapshot(st.session_state.session_id, save['save_id'])
                            session = db_manager.get_session(st.session_state.session_id)
                            st.session_state.messages = []
                            for msg in db_manager.get_chat_history(st.session_state.session_id):
                                st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
                            st.session_state.game_chain = build_novel_chain(st.session_state.novel_title)
                            st.rerun()
                        if st.button("🗑️ 删除存档", key=f"del_{save['save_id']}", use_container_width=True):
                            with db_manager.get_conn() as conn:
                                conn.execute("DELETE FROM game_saves WHERE save_id=?", (save['save_id'],))
                            st.rerun()
            else:
                st.markdown(
                    '<div class="empty-state" style="padding:1rem"><p style="font-size:0.85rem">暂无存档</p></div>',
                    unsafe_allow_html=True,
                )

            if st.button("💾 手动存档", use_container_width=True):
                save_name = f"存档_{datetime.now().strftime('%m%d_%H%M')}"
                db_manager.save_game_snapshot(st.session_state.session_id, save_name)
                st.toast(f"✅ 已保存为「{save_name}」")
                st.rerun()

    st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)
    st.markdown(
        """<div style="text-align:center;color:var(--text-muted);font-size:0.75rem">
            AI互动小说引擎 v3.0<br>
            LangChain + Streamlit
        </div>""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero-section">
        <h1 class="hero-title glow animate-float">🎭 沉浸式多角色互动小说引擎</h1>
        <p class="hero-subtitle">由AI驱动的沉浸式文字冒险游戏 · 每一次选择都是独一无二的旅程</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.session_id:
    st.markdown(
        """<div class="empty-state" style="padding:1rem 0 0.5rem 0">
            <p style="font-size:1.3rem;color:var(--primary-light);font-weight:600">🎮 开始你的冒险</p>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        features = [
            ("🗺️ 探索", "探索未知的世界，发现隐藏的秘密"),
            ("💬 对话", "与NPC对话，获取信息和任务"),
            ("⚔️ 战斗", "参与战斗，提升实力"),
            ("🔍 收集", "收集线索，揭开世界的秘密"),
            ("🎭 自由", "你的每个选择都会影响故事走向"),
        ]

        for icon, desc in features:
            st.markdown(
                f"""<div class="feature-item">
                    <span style="font-size:1.1rem;margin-right:8px">{icon}</span>
                    <span style="color:var(--text-secondary)"><strong style="color:var(--text-primary)">{desc.split('，')[0] if '，' in desc else desc}</strong>
                    {"，" + "，".join(desc.split("，")[1:]) if "，" in desc else ""}</span>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)

        st.markdown(
            """<div style="text-align:center;color:var(--text-muted);padding:0.5rem">
                <p style="font-size:1rem">👈 <strong style="color:var(--text-secondary)">在左侧选择一个世界开始冒险</strong></p>
                <p style="font-size:0.8rem;margin-top:0.3rem">支持手机、平板和电脑访问</p>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("描述你的行动..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("✨ AI正在构思故事..."):
                try:
                    if st.session_state.game_chain is None:
                        st.session_state.game_chain = build_novel_chain(
                            st.session_state.novel_title
                        )
                    response = st.session_state.game_chain({
                        "session_id": st.session_state.session_id,
                        "input": prompt,
                    })
                    st.markdown(response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"❌ 抱歉，发生了错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
