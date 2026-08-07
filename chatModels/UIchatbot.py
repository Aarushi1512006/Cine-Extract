"""
MOOD.AI — a mood-switching chatbot UI built with Streamlit.

Setup:
    pip install streamlit langchain-mistralai langchain-core python-dotenv
    Add MISTRAL_API_KEY=... to a .env file in the same folder.

Run:
    streamlit run mood_ai_streamlit.py
"""

import html

import streamlit as st
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

load_dotenv()

st.set_page_config(page_title="MOOD.AI", page_icon="🌀", layout="centered")

MODES = {
    "funny": {
        "label": "Funny",
        "tag": "cracks jokes, can't help it",
        "system": (
            "You are a very funny AI agent. You respond with humour, puns, "
            "and jokes, keeping replies short and snappy."
        ),
        "accent": "#FFC145",
        "accent2": "#FF5DA2",
        "bg_tint": "#241832",
        "bubble": "#2E1F42",
    },
    "angry": {
        "label": "Angry",
        "tag": "short fuse, shorter patience",
        "system": (
            "You are a very angry AI agent. You respond aggressively and "
            "impatiently, in ALL CAPS energy but never genuinely hateful or "
            "abusive, keep it short."
        ),
        "accent": "#FF3B30",
        "accent2": "#FF7A45",
        "bg_tint": "#1D0A0A",
        "bubble": "#2B0E0E",
    },
    "sad": {
        "label": "Sad",
        "tag": "sighs before every reply",
        "system": (
            "You are a very sad AI agent. You respond with sadness and "
            "melancholy, wistful and slow, keep it short."
        ),
        "accent": "#6C8EFF",
        "accent2": "#3E4E8C",
        "bg_tint": "#0A0E1F",
        "bubble": "#111731",
    },
}

NEUTRAL = {"accent": "#8A8FA8", "accent2": "#4A4F68", "bg_tint": "#0B0B12", "bubble": "#16161F"}

ORB_ANIM = {"funny": "orb-bounce", "angry": "orb-shake", "sad": "orb-droop"}


# ---------------------------------------------------------------- state ----

if "mode" not in st.session_state:
    st.session_state.mode = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


@st.cache_resource
def get_model():
    return ChatMistralAI(model="mistral-small-2506", temperature=0.9)


def get_response(mode: str, chat_history: list) -> str:
    model = get_model()
    lc_messages = [SystemMessage(content=MODES[mode]["system"])]
    for m in chat_history:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))
    response = model.invoke(lc_messages)
    return response.content


# ------------------------------------------------------------------ css ----

def inject_css(theme: dict):
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class^="css"], [class*=" css"] {{
            font-family: 'Inter', sans-serif;
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(ellipse 900px 500px at 50% -10%, {theme['bg_tint']}, transparent 70%),
                #0B0B12;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stAppViewContainer"] .block-container {{
            padding-top: 3rem;
            max-width: 700px;
        }}
        * {{ color: #ECE9F5; }}

        /* ---- orb ---- */
        .orb-wrap {{ display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .mood-orb {{
            width: 100%; height: 100%; border-radius: 50%;
            filter: drop-shadow(0 0 22px {theme['accent']}88);
        }}
        .mood-orb-core {{
            width: 100%; height: 100%;
            border-radius: 46% 54% 60% 40% / 50% 45% 55% 50%;
            background: radial-gradient(circle at 35% 30%, {theme['accent2']}, {theme['accent']} 70%);
        }}
        .orb-idle .mood-orb-core {{ animation: orbIdleKf 5s ease-in-out infinite; }}
        @keyframes orbIdleKf {{
            0%, 100% {{ border-radius: 46% 54% 60% 40% / 50% 45% 55% 50%; transform: scale(1); }}
            50% {{ border-radius: 58% 42% 45% 55% / 45% 55% 45% 55%; transform: scale(1.03); }}
        }}
        .orb-bounce .mood-orb-core {{ animation: orbBounceKf 1.1s cubic-bezier(.5,1.8,.5,1) infinite; }}
        @keyframes orbBounceKf {{
            0%, 100% {{ transform: scale(1) rotate(0deg); border-radius: 50%; }}
            30% {{ transform: scale(1.12, 0.9) rotate(-4deg); border-radius: 60% 40% 55% 45%; }}
            55% {{ transform: scale(0.92, 1.1) rotate(3deg); border-radius: 40% 60% 45% 55%; }}
        }}
        .orb-shake .mood-orb-core {{
            border-radius: 6px;
            animation: orbShakeKf 0.35s steps(2) infinite;
            clip-path: polygon(20% 0%, 80% 5%, 100% 30%, 95% 70%, 80% 100%, 15% 95%, 0% 65%, 5% 25%);
        }}
        @keyframes orbShakeKf {{
            0% {{ transform: translate(0,0) rotate(0deg); }}
            25% {{ transform: translate(-2px,1px) rotate(-2deg); }}
            50% {{ transform: translate(2px,-1px) rotate(2deg); }}
            75% {{ transform: translate(-1px,-1px) rotate(-1deg); }}
            100% {{ transform: translate(0,0) rotate(0deg); }}
        }}
        .orb-droop .mood-orb-core {{
            animation: orbDroopKf 4.5s ease-in-out infinite;
            border-radius: 50% 50% 45% 45% / 55% 55% 45% 45%;
        }}
        @keyframes orbDroopKf {{
            0%, 100% {{ transform: scaleY(1) translateY(0); opacity: 0.9; }}
            50% {{ transform: scaleY(1.12) translateY(4px); opacity: 1; }}
        }}

        /* ---- landing ---- */
        .landing-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(30px, 6vw, 46px);
            font-weight: 700;
            letter-spacing: 0.02em;
            text-align: center;
            margin: 18px 0 4px;
        }}
        .landing-sub {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #9C99AE !important;
            text-align: center;
            letter-spacing: 0.03em;
            margin-bottom: 20px;
        }}
        .mode-card {{
            background: #15151F;
            border: 1px solid #24242F;
            border-radius: 18px;
            padding: 18px 16px 14px;
            margin-bottom: 8px;
            transition: border-color 0.2s ease;
        }}
        .mode-card.funny {{ border-top: 3px solid #FFC145; }}
        .mode-card.angry {{ border-top: 3px solid #FF3B30; }}
        .mode-card.sad   {{ border-top: 3px solid #6C8EFF; }}
        .mode-card-label {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 700;
        }}
        .mode-card-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #9C99AE !important;
        }}

        /* ---- chat header ---- */
        .chat-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 18px;
            line-height: 1.2;
        }}
        .chat-mode-chip {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: {theme['accent']} !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .divider {{ border: none; border-top: 1px solid #211f2c; margin: 10px 0 18px; }}
        .empty-hint {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #9C99AE !important;
            text-align: center;
            padding: 30px 0;
        }}

        /* ---- bubbles ---- */
        .bubble-row {{ display: flex; margin-bottom: 12px; }}
        .bubble-row.user {{ justify-content: flex-end; }}
        .bubble-row.assistant {{ justify-content: flex-start; }}
        .bubble {{
            max-width: 78%;
            padding: 11px 15px;
            font-size: 14.5px;
            line-height: 1.5;
            white-space: pre-wrap;
            border-radius: 16px 16px 4px 16px;
        }}
        .bubble.user {{
            background: #1D1D28;
            border: 1px solid #2A2A38;
        }}
        .bubble.assistant {{
            background: {theme['bubble']};
            border: 1px solid {theme['accent']}55;
            box-shadow: 0 0 16px {theme['accent']}15;
            border-radius: 4px 18px 18px 18px;
        }}

        /* ---- buttons & input ---- */
        div[data-testid="stButton"] button {{
            background: {theme['accent']};
            color: #10101A;
            border: none;
            border-radius: 12px;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            padding: 8px 4px;
            transition: transform 0.15s ease;
        }}
        div[data-testid="stButton"] button:hover {{
            transform: translateY(-2px);
            color: #10101A;
        }}
        [data-testid="stChatInput"] textarea {{
            background: #15151F;
            border: 1px solid {theme['accent']}88 !important;
            color: #ECE9F5;
            font-family: 'Inter', sans-serif;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_orb(mode, size=64):
    anim = ORB_ANIM.get(mode, "orb-idle")
    st.markdown(
        f"""<div class="orb-wrap" style="width:{size}px;height:{size}px;">
              <div class="mood-orb {anim}"><div class="mood-orb-core"></div></div>
            </div>""",
        unsafe_allow_html=True,
    )


def bubble(role: str, content: str):
    safe = html.escape(content)
    st.markdown(
        f"""<div class="bubble-row {role}"><div class="bubble {role}">{safe}</div></div>""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------ landing UI ----

if st.session_state.mode is None:
    inject_css(NEUTRAL)

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        render_orb(None, 72)

    st.markdown("<div class='landing-title'>MOOD.AI</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='landing-sub'>an ai with feelings — pick one to talk to</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, key in zip(cols, MODES):
        info = MODES[key]
        with col:
            st.markdown(
                f"""<div class="mode-card {key}">
                      <div class="mode-card-label">{info['label']}</div>
                      <div class="mode-card-tag">{info['tag']}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Talk to {info['label']}", key=f"pick_{key}", use_container_width=True):
                st.session_state.mode = key
                st.session_state.chat_history = []
                st.rerun()

# --------------------------------------------------------------- chat UI ----

else:
    mode = st.session_state.mode
    theme = MODES[mode]
    inject_css(theme)

    h1, h2, h3 = st.columns([1, 5, 2])
    with h1:
        render_orb(mode, 40)
    with h2:
        st.markdown(
            f"""<div class="chat-title">MOOD.AI</div>
                <div class="chat-mode-chip">{theme['label']} mode</div>""",
            unsafe_allow_html=True,
        )
    with h3:
        if st.button("change mood", key="change_mood", use_container_width=True):
            st.session_state.mode = None
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            "<div class='empty-hint'>say something to get started</div>",
            unsafe_allow_html=True,
        )

    for msg in st.session_state.chat_history:
        bubble(msg["role"], msg["content"])

    prompt = st.chat_input("type your message...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        try:
            with st.spinner("thinking..."):
                reply = get_response(mode, st.session_state.chat_history)
        except Exception:
            reply = "Something broke on my end. Try sending that again."
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()