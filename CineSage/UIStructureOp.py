"""
CineExtract — Movie Info Extractor
-----------------------------------
Paste a paragraph about a movie, and this app uses Mistral AI (via LangChain)
to extract structured movie data, then renders it as a rich, magazine-style
movie profile page.

Run with: streamlit run movie_extractor_app.py
"""

import os
import json
import random

import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()

# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------

class Movie(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str


parser = PydanticOutputParser(pydantic_object=Movie)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    Extract movie information from the paragraph.
    {format_instructions}
    """,
        ),
        ("human", "{paragraph}"),
    ]
)

# --------------------------------------------------------------------------
# Page config + styling
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="CineExtract — Movie Info Extractor",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #0F0F12;
    --surface: #1E1E24;
    --text: #FFFFFF;
    --muted: #A0A0A5;
    --accent: #E50914;
    --accent-2: #E11D48;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header {visibility: hidden;}

.stApp {
    background: var(--bg);
    color: var(--text);
}

/* Streamlit widget accents */
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-2) !important;
}
.stTextArea textarea, .stTextInput input {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid #2c2c34 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* ---------- Input Card ---------- */
.input-card {
    background: var(--surface);
    border: 1px solid #2a2a31;
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.5rem;
}

/* ---------- Hero ---------- */
.hero-wrap {
    position: relative;
    border-radius: 22px;
    overflow: hidden;
    padding: 3.2rem 2.5rem 2.2rem 2.5rem;
    margin-bottom: 2rem;
    background:
        radial-gradient(circle at 15% 15%, rgba(229,9,20,0.30), transparent 55%),
        radial-gradient(circle at 90% 0%, rgba(225,29,72,0.18), transparent 50%),
        linear-gradient(160deg, #17171c 0%, #1a1a20 55%, #0F0F12 100%);
    border: 1px solid #2a2a31;
}

.hero-eyebrow {
    color: var(--accent);
    letter-spacing: 3px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4.2rem;
    line-height: 1;
    letter-spacing: 1px;
    color: var(--text);
    margin-bottom: 0.6rem;
}

.hero-year {
    display: inline-block;
    font-size: 1.1rem;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 1.1rem;
}

.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.4rem;
}

.genre-pill {
    padding: 0.35rem 0.95rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    color: #fff;
    background: var(--accent);
    box-shadow: 0 2px 10px rgba(229,9,20,0.25);
}

.theme-pill {
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--muted);
    background: var(--surface);
    border: 1px solid #2c2c34;
}

/* ---------- Section headers ---------- */
.section-head {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 1px;
    color: var(--text);
    margin: 0 0 0.9rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ---------- Synopsis ---------- */
.synopsis-card {
    background: var(--surface);
    border: 1px solid #2a2a31;
    border-left: 3px solid var(--accent);
    border-radius: 14px;
    padding: 1.5rem 1.7rem;
    font-size: 1.02rem;
    line-height: 1.75;
    color: #E8E8EA;
}

/* ---------- Director banner ---------- */
.director-banner {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    background: var(--surface);
    border: 1px solid #2a2a31;
    border-left: 3px solid var(--accent-2);
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.6rem;
}

.director-avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    color: white;
    flex-shrink: 0;
}

.director-label {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.15rem;
}

.director-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
}

/* ---------- Cast grid ---------- */
.cast-card {
    text-align: center;
    padding: 0.9rem 0.5rem 1rem 0.5rem;
    background: var(--surface);
    border: 1px solid #2a2a31;
    border-radius: 14px;
}

.cast-avatar {
    width: 76px;
    height: 76px;
    border-radius: 50%;
    margin: 0 auto 0.6rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    color: white;
    background: var(--accent);
    border: 2px solid #2c2c34;
}

.cast-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
}

.cast-role {
    font-size: 0.72rem;
    color: var(--muted);
}

/* ---------- Rating ---------- */
.rating-card {
    background: var(--surface);
    border: 1px solid #2a2a31;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

.rating-score {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    color: var(--accent);
    line-height: 1;
}

.rating-label {
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.3rem;
}

hr.divider {
    border: none;
    border-top: 1px solid #2a2a31;
    margin: 2.2rem 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Single accent color for genre pills (Popcorn Red), per the theme's 10% accent rule
GENRE_ACCENT = "#E50914"

# Muted variants of the accent for cast avatars, so they read as a family, not a rainbow
AVATAR_PALETTE = ["#E50914", "#E11D48", "#B0060F", "#C41230", "#8F0710", "#D91A3C"]


def genre_color(g: str) -> str:
    return GENRE_ACCENT


def initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def color_for(name: str) -> str:
    idx = sum(ord(c) for c in name) % len(AVATAR_PALETTE)
    return AVATAR_PALETTE[idx]


def naive_themes(summary: str, genres: List[str]) -> List[str]:
    """Very lightweight theme-tag guesser from summary keywords."""
    theme_keywords = {
        "Ambition": ["ambition", "dream", "rise", "power", "success"],
        "Friendship": ["friend", "bond", "loyalty", "companion"],
        "Betrayal": ["betray", "deceive", "backstab", "traitor"],
        "Redemption": ["redeem", "forgive", "second chance", "atone"],
        "Love": ["love", "romance", "heart", "affection"],
        "Survival": ["survive", "escape", "danger", "fight for"],
        "Family": ["family", "father", "mother", "brother", "sister", "son", "daughter"],
        "Justice": ["justice", "revenge", "law", "crime"],
        "Identity": ["identity", "self-discovery", "who he", "who she"],
        "War": ["war", "battle", "soldier", "army"],
    }
    text = summary.lower()
    found = [tag for tag, kws in theme_keywords.items() if any(k in text for k in kws)]
    if not found:
        found = [g.title() for g in genres[:2]]
    return found[:5]


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

if "movie" not in st.session_state:
    st.session_state.movie = None
if "user_rating" not in st.session_state:
    st.session_state.user_rating = None
if "reviews" not in st.session_state:
    st.session_state.reviews = []


@st.cache_resource(show_spinner=False)
def get_model():
    return ChatMistralAI(model="mistral-small-2506")


def extract_movie(paragraph: str) -> Movie:
    model = get_model()
    final_prompt = prompt.invoke(
        {"paragraph": paragraph, "format_instructions": parser.get_format_instructions()}
    )
    response = model.invoke(final_prompt)
    try:
        return parser.parse(response.content)
    except Exception:
        # fallback: strip code fences and try raw JSON
        raw = response.content.strip().strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
        data = json.loads(raw)
        return Movie(**data)


# --------------------------------------------------------------------------
# Input section
# --------------------------------------------------------------------------

st.markdown(
    "<div class='hero-eyebrow' style='margin-bottom:0.3rem;'>🎬 CINEEXTRACT</div>"
    "<div style='font-family:\"Bebas Neue\",sans-serif;font-size:2.4rem;color:#fff;margin-bottom:1rem;'>"
    "Turn any movie blurb into a full profile</div>",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='input-card'>", unsafe_allow_html=True)
    paragraph = st.text_area(
        "Paste a paragraph about a movie",
        height=140,
        placeholder=(
            "e.g. Inception (2010) is a sci-fi thriller directed by Christopher Nolan, "
            "starring Leonardo DiCaprio, Joseph Gordon-Levitt, and Elliot Page. "
            "It follows a thief who steals secrets through dream-sharing technology..."
        ),
    )
    col_a, col_b = st.columns([1, 5])
    with col_a:
        go = st.button("✨ Extract", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

if go:
    if not paragraph or not paragraph.strip():
        st.warning("Please paste a paragraph describing a movie first.")
    else:
        with st.spinner("Analyzing the paragraph and extracting movie data..."):
            try:
                st.session_state.movie = extract_movie(paragraph)
                st.session_state.user_rating = None
                st.session_state.reviews = []
            except Exception as e:
                st.session_state.movie = None
                st.error(f"Couldn't extract movie data: {e}")

# --------------------------------------------------------------------------
# Output — movie profile
# --------------------------------------------------------------------------

movie: Optional[Movie] = st.session_state.movie

if movie:
    themes = naive_themes(movie.summary, movie.genre)

    # ---------------- Hero ----------------
    genre_html = "".join(
        f"<span class='genre-pill' style='background:{genre_color(g)}'>{g}</span>"
        for g in movie.genre
    )
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-eyebrow">Now Extracted</div>
            <div class="hero-title">{movie.title}</div>
            <div class="hero-year">{movie.release_year if movie.release_year else "Year Unknown"}</div>
            <div class="badge-row">{genre_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1], gap="large")

    with left:
        # ---------------- Synopsis ----------------
        st.markdown("<div class='section-head'>📝 Synopsis</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='synopsis-card'>{movie.summary}</div>", unsafe_allow_html=True)

        theme_html = "".join(f"<span class='theme-pill'>#{t}</span>" for t in themes)
        st.markdown(
            f"<div style='margin-top:0.9rem;' class='badge-row'>{theme_html}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # ---------------- Director ----------------
        st.markdown("<div class='section-head'>🎥 Creative Core</div>", unsafe_allow_html=True)
        director_name = movie.director if movie.director else "Unknown Director"
        st.markdown(
            f"""
            <div class="director-banner">
                <div class="director-avatar">{initials(director_name)}</div>
                <div>
                    <div class="director-label">Director</div>
                    <div class="director-name">{director_name}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---------------- Cast grid ----------------
        if movie.cast:
            st.markdown("<div class='section-head' style='font-size:1.15rem;'>👥 Cast</div>", unsafe_allow_html=True)
            cast_cols = st.columns(min(4, len(movie.cast)) or 1)
            for i, actor in enumerate(movie.cast):
                with cast_cols[i % len(cast_cols)]:
                    st.markdown(
                        f"""
                        <div class="cast-card">
                            <div class="cast-avatar" style="background:{color_for(actor)};">
                                {initials(actor)}
                            </div>
                            <div class="cast-name">{actor}</div>
                            <div class="cast-role">Cast</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.caption("No cast information found.")

    with right:
        # ---------------- Ratings ----------------
        st.markdown("<div class='section-head'>📊 Audience</div>", unsafe_allow_html=True)

        if movie.rating is not None:
            st.markdown(
                f"""
                <div class="rating-card">
                    <div class="rating-score">★ {movie.rating}</div>
                    <div class="rating-label">Community Rating</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            if st.session_state.user_rating is None:
                st.markdown(
                    """
                    <div class="rating-card">
                        <div class="rating-label" style="margin-bottom:0.6rem;">No rating yet</div>
                    """,
                    unsafe_allow_html=True,
                )
                stars = st.feedback("stars", key="rating_widget")
                if stars is not None:
                    st.session_state.user_rating = stars + 1
                    st.rerun()
                st.caption("Be the first to rate this movie!")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"""
                    <div class="rating-card">
                        <div class="rating-score">★ {st.session_state.user_rating}.0</div>
                        <div class="rating-label">Your Rating</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        # ---------------- Review box ----------------
        st.markdown("<div class='section-head' style='font-size:1.15rem;'>💬 Reviews</div>", unsafe_allow_html=True)
        with st.form("review_form", clear_on_submit=True):
            reviewer = st.text_input("Your name", placeholder="Anonymous")
            review_text = st.text_area("Write a short review", height=90)
            submitted = st.form_submit_button("Submit review", use_container_width=True)
            if submitted and review_text.strip():
                st.session_state.reviews.insert(
                    0, {"name": reviewer.strip() or "Anonymous", "text": review_text.strip()}
                )

        for rev in st.session_state.reviews:
            st.markdown(
                f"""
                <div style="background:#1E1E24;border:1px solid #2a2a31;border-left:3px solid #E50914;
                            border-radius:12px;padding:0.8rem 1rem;margin-bottom:0.6rem;">
                    <div style="font-weight:600;font-size:0.85rem;color:#fff;">{rev['name']}</div>
                    <div style="font-size:0.85rem;color:#A0A0A5;margin-top:0.2rem;">{rev['text']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem;color:#8b93ba;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🎞️</div>
            Paste a movie description above and hit <b>Extract</b> to see the profile.
        </div>
        """,
        unsafe_allow_html=True,
    )