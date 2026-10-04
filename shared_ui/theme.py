from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import Literal

import streamlit as st


Surface = Literal["auth", "user", "admin"]
ASSET_DIR = Path(__file__).resolve().parent / "assets"


@lru_cache(maxsize=4)
def _asset_data_uri(filename: str) -> str:
    path = ASSET_DIR / filename
    if not path.exists():
        return ""
    media_type = "image/webp" if path.suffix.lower() == ".webp" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def inject_theme(surface: Surface = "user") -> None:
    accent = "#6D28D9" if surface == "admin" else "#2563EB"
    accent_alt = "#2563EB" if surface == "admin" else "#7C3AED"
    desktop_image = _asset_data_uri("auth-collaboration-desktop.webp")
    mobile_image = _asset_data_uri("auth-collaboration-mobile.webp")
    desktop_url = f'url("{desktop_image}")' if desktop_image else "none"
    mobile_url = f'url("{mobile_image}")' if mobile_image else desktop_url

    css = _BASE_CSS.replace("__ACCENT__", accent).replace(
        "__ACCENT_ALT__", accent_alt
    )
    if surface == "auth":
        css += _AUTH_CSS.replace("__DESKTOP_IMAGE__", desktop_url).replace(
            "__MOBILE_IMAGE__", mobile_url
        )
    elif surface == "admin":
        css += _ADMIN_CSS
    else:
        css += _USER_CSS
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_BASE_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,500,0,0');
:root {
    color-scheme: light;
    --zl-canvas: #F4F7FB; --zl-surface: #FFFFFF; --zl-surface-alt: #F8FAFC;
    --zl-navy: #0B1730; --zl-ink: #14213D; --zl-muted: #64748B;
    --zl-line: #DCE4EF; --zl-brand: __ACCENT__; --zl-brand-alt: __ACCENT_ALT__;
    --zl-cyan: #0891B2; --zl-violet: #7C3AED; --zl-success: #059669;
    --zl-warning: #D97706; --zl-danger: #DC2626;
    --zl-shadow-sm: 0 5px 18px rgba(20,33,61,.06);
    --zl-shadow-md: 0 14px 34px rgba(20,33,61,.12);
}
html { scroll-behavior: smooth; }
body, .stApp, button, input, textarea, select { font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif; }
.stApp { background: var(--zl-canvas); color: var(--zl-ink); }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 4rem; }
.block-container > div:first-child { animation: zl-page-enter 240ms cubic-bezier(.22,1,.36,1) both; will-change: opacity, transform; }
p, label, [data-testid="stCaptionContainer"] { color: var(--zl-muted); }
h1, h2, h3 { color: var(--zl-ink); letter-spacing: 0; font-family: "Manrope", "Noto Sans SC", sans-serif; }
h1 { font-size: 2.15rem !important; line-height: 1.18 !important; }
h2 { font-size: 1.42rem !important; } h3 { font-size: 1.06rem !important; }
a { color: var(--zl-brand); }
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    min-height: 2.6rem; border-radius: 8px; border: 1px solid #B8C5D8;
    background: var(--zl-surface); color: var(--zl-ink); font-weight: 700;
    letter-spacing: 0; box-shadow: none;
    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, color 160ms ease, box-shadow 160ms ease, filter 160ms ease;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    color: var(--zl-brand); border-color: var(--zl-brand); background: #F3F7FF;
    transform: translateY(-1px); box-shadow: 0 7px 16px rgba(37,99,235,.12);
}
div[data-testid="stButton"] > button:active,
div[data-testid="stFormSubmitButton"] > button:active { transform: translateY(0); }
button:focus-visible, a:focus-visible, [role="radio"]:focus-visible,
summary:focus-visible { outline: 3px solid #60A5FA !important; outline-offset: 3px; }
div[data-testid="stButton"] > button p,
div[data-testid="stFormSubmitButton"] > button p,
div[data-testid="stDownloadButton"] > button p { color: inherit !important; }
div[data-testid="stButton"] > button[kind^="primary"],
div[data-testid="stFormSubmitButton"] > button[kind^="primary"] {
    color: #FFF; border-color: transparent;
    background: linear-gradient(112deg, var(--zl-brand), var(--zl-brand-alt));
    box-shadow: 0 9px 20px color-mix(in srgb, var(--zl-brand) 22%, transparent);
}
div[data-testid="stButton"] > button[kind^="primary"] p,
div[data-testid="stFormSubmitButton"] > button[kind^="primary"] p { color: #FFF !important; }
div[data-testid="stButton"] > button[kind^="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind^="primary"]:hover {
    color: #FFF; filter: brightness(1.08);
    box-shadow: 0 12px 25px color-mix(in srgb, var(--zl-brand) 30%, transparent);
}
div[data-testid="stButton"] > button:disabled,
div[data-testid="stFormSubmitButton"] > button:disabled {
    color: #7A8799 !important; background: #E8EDF5 !important;
    border-color: #D8E0EB !important; box-shadow: none !important; transform: none !important;
}
.st-key-logout_button button, [class*="st-key-danger_"] button {
    color: var(--zl-danger) !important; background: rgba(220,38,38,.08) !important;
    border-color: rgba(220,38,38,.42) !important;
}
.st-key-logout_button button:hover, [class*="st-key-danger_"] button:hover {
    color: #FFF !important; background: var(--zl-danger) !important; border-color: var(--zl-danger) !important;
}
[class*="st-key-success_"] button, [class*="st-key-interested_"] button:disabled {
    color: #FFF !important; background: #047857 !important;
    border-color: #047857 !important; opacity: 1 !important;
}
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-baseweb="select"] > div {
    color: var(--zl-ink) !important; background: var(--zl-surface) !important;
    border: 1px solid #B8C5D8 !important; border-radius: 8px !important; box-shadow: none !important;
    transition: border-color 160ms ease, box-shadow 160ms ease;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--zl-brand) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--zl-brand) 14%, transparent) !important;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-baseweb="select"] * { color: var(--zl-ink) !important; -webkit-text-fill-color: var(--zl-ink) !important; }
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #64748B !important; -webkit-text-fill-color: #64748B !important; }
div[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--zl-surface); border-color: var(--zl-line) !important;
    border-radius: 8px !important; box-shadow: var(--zl-shadow-sm);
}
[data-testid="stExpander"] summary {
    min-height: 2.65rem; border-radius: 7px; color: var(--zl-ink);
    transition: color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}
[data-testid="stExpander"] summary:hover {
    color: var(--zl-brand); background: color-mix(in srgb, var(--zl-brand) 5%, transparent);
}
[data-testid="stExpander"] summary p {
    color: inherit !important; transition: color 180ms ease;
}
[data-testid="stExpander"] summary:focus-visible {
    outline: 3px solid color-mix(in srgb, var(--zl-brand) 45%, transparent) !important;
    outline-offset: 2px;
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
    display: inline-block; width: 1.25rem; height: 1.25rem; overflow: hidden;
    color: transparent !important; font-size: 0 !important;
    transform-origin: center; transition: transform 180ms ease, color 180ms ease;
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::before {
    content: "keyboard_arrow_right"; display: block; color: currentColor;
    font-family: "Material Symbols Rounded"; font-size: 1.25rem; line-height: 1.25rem;
    -webkit-font-feature-settings: "liga"; font-feature-settings: "liga";
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::before {
    color: var(--zl-muted);
}
[data-testid="stExpander"] summary:hover [data-testid="stIconMaterial"]::before,
[data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"]::before {
    color: var(--zl-brand);
}
[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpander"] details[open] summary {
    color: var(--zl-brand);
}
[data-testid="stExpander"] details[open] > summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"] {
    transform: rotate(90deg);
}
[data-testid="stExpander"] details[open] > div[data-testid="stExpanderDetails"] {
    animation: zl-expander-enter 220ms cubic-bezier(.22,1,.36,1) both;
    transform-origin: top center;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    border-color: color-mix(in srgb, var(--zl-brand) 32%, var(--zl-line)) !important;
    box-shadow: var(--zl-shadow-md);
}
[data-testid="stVerticalBlock"][class*="st-key-match_card_"],
[data-testid="stVerticalBlock"][class*="st-key-project_card_"],
[data-testid="stVerticalBlock"][class*="st-key-candidate_card_"],
[data-testid="stVerticalBlock"][class*="st-key-my_match_card_"],
[data-testid="stVerticalBlock"][class*="st-key-favorite_card_"],
[data-testid="stVerticalBlock"][class*="st-key-quick_"] {
    --card-accent: var(--zl-brand);
    background: var(--zl-surface); border: 1px solid var(--zl-line);
    border-left: 4px solid var(--card-accent); border-radius: 8px;
    box-shadow: var(--zl-shadow-sm);
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}
[data-testid="stVerticalBlock"][class*="st-key-match_card_"]:hover,
[data-testid="stVerticalBlock"][class*="st-key-project_card_"]:hover,
[data-testid="stVerticalBlock"][class*="st-key-favorite_card_"]:hover,
[data-testid="stVerticalBlock"][class*="st-key-quick_"]:hover {
    transform: translateY(-2px); box-shadow: var(--zl-shadow-md);
    border-color: var(--card-accent);
}
[data-testid="stVerticalBlock"][class*="_score_green"],
[data-testid="stVerticalBlock"][class*="_state_green"] { --card-accent: #059669; }
[data-testid="stVerticalBlock"][class*="_score_slate"],
[data-testid="stVerticalBlock"][class*="_state_slate"] { --card-accent: #64748B; }
[data-testid="stVerticalBlock"][class*="_state_amber"] { --card-accent: #D97706; }
[data-testid="stVerticalBlock"][class*="_state_red"] { --card-accent: #DC2626; }
[data-testid="stMetric"] {
    background: var(--zl-surface); border: 1px solid var(--zl-line); border-radius: 8px;
    padding: 1rem; box-shadow: var(--zl-shadow-sm);
}
[data-testid="stMetricLabel"] { color: var(--zl-muted); } [data-testid="stMetricValue"] { color: var(--zl-ink); }
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, var(--zl-brand), var(--zl-cyan));
    transition: width 600ms cubic-bezier(.22,1,.36,1);
}
[data-testid="stDataFrame"] { border: 1px solid var(--zl-line); border-radius: 8px; overflow: hidden; box-shadow: var(--zl-shadow-sm); }
[data-testid="stAlert"] { border-radius: 8px; animation: zl-feedback-enter 180ms ease-out both; }
[data-baseweb="tab-list"] { gap: 1.1rem; border-bottom: 1px solid var(--zl-line); }
[data-baseweb="tab"] { height: 2.7rem; } [data-baseweb="tab"] p { color: var(--zl-muted); font-weight: 700; }
[aria-selected="true"][data-baseweb="tab"] p { color: var(--zl-brand); }
hr { border-color: var(--zl-line) !important; }
.material-symbols-rounded {
    font-family: "Material Symbols Rounded"; font-weight: normal; font-style: normal;
    font-size: 1.35rem; line-height: 1; letter-spacing: normal; text-transform: none;
    display: inline-block; white-space: nowrap; word-wrap: normal; direction: ltr;
    -webkit-font-feature-settings: "liga"; -webkit-font-smoothing: antialiased;
}
.zl-brand-lockup { display: flex; align-items: center; gap: .82rem; margin: .2rem 0 1rem; }
.zl-brand-mark { width: 42px; height: 42px; position: relative; flex: 0 0 42px; }
.zl-brand-mark span { position: absolute; width: 12px; height: 12px; border-radius: 50%; background: var(--zl-brand); box-shadow: 0 0 18px color-mix(in srgb, var(--zl-brand) 40%, transparent); }
.zl-brand-mark span:nth-child(1) { left: 2px; top: 15px; }
.zl-brand-mark span:nth-child(2) { right: 2px; top: 3px; background: var(--zl-cyan); }
.zl-brand-mark span:nth-child(3) { right: 4px; bottom: 3px; background: var(--zl-brand-alt); }
.zl-brand-mark::before, .zl-brand-mark::after { content: ""; position: absolute; height: 1px; background: #8FA5C7; transform-origin: left center; }
.zl-brand-mark::before { width: 30px; left: 8px; top: 20px; transform: rotate(-31deg); }
.zl-brand-mark::after { width: 29px; left: 8px; top: 22px; transform: rotate(30deg); }
.zl-brand-name { color: var(--zl-ink); font: 700 1.16rem/1.2 "Manrope", "Noto Sans SC", sans-serif; }
.zl-brand-name strong { color: var(--zl-brand); }
.zl-brand-subtitle { color: var(--zl-muted); font-size: .78rem; margin-top: .1rem; }
.zl-brand-lockup--compact { margin-bottom: .45rem; }
.zl-brand-lockup--compact .zl-brand-mark { transform: scale(.82); transform-origin: left center; margin-right: -.35rem; }
.zl-brand-lockup--inverse .zl-brand-name { color: #FFF; }
.zl-brand-lockup--inverse .zl-brand-subtitle { color: #B9C8E2; }
.zl-page-intro { margin: .2rem 0 1.45rem; max-width: 780px; }
.zl-eyebrow { color: var(--zl-brand); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .48rem; }
.zl-page-intro h1 { margin: 0; } .zl-page-intro p { margin: .48rem 0 0; color: var(--zl-muted); font-size: .96rem; }
.zl-metric-tile { --tile-accent: var(--zl-brand); position: relative; min-height: 142px; padding: 1.05rem 1.1rem 1rem; border: 1px solid var(--zl-line); border-radius: 8px; background: var(--zl-surface); box-shadow: var(--zl-shadow-sm); overflow: hidden; transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease; }
.zl-metric-tile:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--tile-accent) 35%, var(--zl-line)); box-shadow: var(--zl-shadow-md); }
.zl-metric-topline { position: absolute; left: 0; top: 0; right: 0; height: 4px; background: var(--tile-accent); }
.zl-metric-icon { position: absolute; right: 1rem; top: 1rem; color: var(--tile-accent); width: 32px; height: 32px; display: grid; place-items: center; border-radius: 8px; background: color-mix(in srgb, var(--tile-accent) 10%, white); }
.zl-metric-label { color: var(--zl-muted); font-size: .82rem; font-weight: 700; margin-top: .35rem; }
.zl-metric-value { color: var(--tile-accent); font: 800 2rem/1.15 "Manrope", sans-serif; margin-top: .58rem; }
.zl-metric-caption { color: var(--zl-muted); font-size: .76rem; margin-top: .3rem; }
.zl-empty-state { padding: 2rem 1.25rem; text-align: center; border: 1px dashed #B8C5D8; border-radius: 8px; background: linear-gradient(180deg,#FFF,#F8FAFC); }
.zl-empty-state > .material-symbols-rounded { color: var(--zl-brand); font-size: 2.2rem; width: 56px; height: 56px; display: grid; place-items: center; margin: 0 auto .6rem; border-radius: 50%; background: color-mix(in srgb, var(--zl-brand) 9%, white); }
.zl-empty-title { color: var(--zl-ink); font-weight: 800; }
.zl-empty-description { color: var(--zl-muted); font-size: .88rem; margin-top: .32rem; }
.zl-status-badge { --badge-color: var(--zl-muted); display: inline-flex; align-items: center; min-height: 26px; padding: .2rem .62rem; border: 1px solid color-mix(in srgb,var(--badge-color) 30%,transparent); border-radius: 999px; color: color-mix(in srgb,var(--badge-color) 75%,#0B1730); background: color-mix(in srgb,var(--badge-color) 9%,white); font-size: .76rem; font-weight: 800; }
.zl-score-wrap { display: flex; align-items: center; justify-content: center; min-height: 116px; }
.zl-score-ring { --score: 0; --score-color: var(--zl-brand); width: 108px; height: 108px; padding: 8px; border-radius: 50%; background: conic-gradient(var(--score-color) calc(var(--score)*1%),#E5EAF2 0); box-shadow: 0 9px 24px color-mix(in srgb,var(--score-color) 16%,transparent); animation: zl-score-enter 600ms cubic-bezier(.22,1,.36,1) both; }
.zl-score-core { width: 100%; height: 100%; border-radius: 50%; background: var(--zl-surface); display: flex; flex-direction: column; align-items: center; justify-content: center; }
.zl-score-core strong { color: color-mix(in srgb,var(--score-color) 75%,#0B1730); font: 800 1.45rem/1 "Manrope",sans-serif; }
.zl-score-core span { color: var(--zl-muted); font-size: .66rem; margin-top: .32rem; }
.zl-score-wrap--small .zl-score-ring { width: 88px; height: 88px; padding: 7px; }
.zl-score-wrap--small .zl-score-core strong { font-size: 1.15rem; }
.zl-dimension-list { display: grid; gap: .68rem; margin: .9rem 0; }
.zl-dimension-meta { display: flex; justify-content: space-between; align-items: center; color: var(--zl-muted); font-size: .8rem; }
.zl-dimension-meta strong { color: var(--zl-ink); }
.zl-dimension-track { height: 7px; border-radius: 999px; background: #E7EDF5; overflow: hidden; }
.zl-dimension-track > span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg,color-mix(in srgb,var(--bar-color) 72%,white),var(--bar-color)); animation: zl-bar-enter 600ms cubic-bezier(.22,1,.36,1) both; transform-origin: left; }
.zl-skeleton { display: grid; gap: .7rem; padding: 1rem; border: 1px solid var(--zl-line); border-radius: 8px; background: var(--zl-surface); }
.zl-skeleton-line { position: relative; display: block; overflow: hidden; width: var(--line-width); height: 12px; border-radius: 4px; background: #E8EDF4; }
.zl-skeleton-line::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg,transparent,#F5F7FA,transparent); animation: zl-shimmer 1.35s ease-in-out infinite; }
.zl-section { margin: 1.8rem 0 .78rem; }
.zl-section-title { color: var(--zl-ink); font-size: 1.12rem; font-weight: 800; }
.zl-section-caption { color: var(--zl-muted); font-size: .86rem; margin-top: .2rem; }
.zl-pill { display: inline-block; max-width: 100%; overflow-wrap: anywhere; padding: .22rem .58rem; margin: .14rem .18rem .14rem 0; border: 1px solid #CFE0FF; border-radius: 999px; color: #1D4ED8; background: #EFF5FF; font-size: .78rem; font-weight: 700; }
.zl-detail-band { padding: .85rem 1rem; margin: .55rem 0 1.25rem; border-left: 4px solid var(--zl-brand); border-radius: 0 8px 8px 0; color: #334865; background: #EDF4FF; }
.zl-notification { position: relative; padding: 1rem 1.05rem 1rem 1.3rem; margin: .68rem 0; border: 1px solid var(--zl-line); border-radius: 8px; background: var(--zl-surface); box-shadow: var(--zl-shadow-sm); }
.zl-notification::before { content: ""; position: absolute; left: .55rem; top: 1.3rem; width: 6px; height: 6px; border-radius: 50%; background: #B5C1D2; }
.zl-notification-unread::before { background: var(--zl-brand); box-shadow: 0 0 0 5px color-mix(in srgb,var(--zl-brand) 10%,transparent); }
.zl-notification-title { color: var(--zl-ink); font-weight: 800; margin-bottom: .26rem; }
.zl-notification-content { color: #465874; margin-bottom: .42rem; }
.zl-notification-time { color: var(--zl-muted); font-size: .76rem; }
@keyframes zl-page-enter { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: translateY(0); } }
@keyframes zl-expander-enter { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
@keyframes zl-feedback-enter { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
@keyframes zl-score-enter { from { opacity: .25; transform: scale(.92) rotate(-8deg); } to { opacity: 1; transform: scale(1) rotate(0); } }
@keyframes zl-bar-enter { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes zl-shimmer { from { transform: translateX(-100%); } to { transform: translateX(100%); } }
@media (max-width: 1199px) {
    .block-container { max-width: 1000px; padding-left: 1.4rem; padding-right: 1.4rem; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .8rem; }
    [data-testid="stColumn"], [data-testid="column"] { min-width: min(100%,260px) !important; flex: 1 1 calc(50% - .8rem) !important; }
    .zl-metric-tile { min-height: 134px; }
}
@media (max-width: 767px) {
    .block-container { padding: 1.15rem .9rem 3rem; } h1 { font-size: 1.75rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .7rem; }
    [data-testid="stColumn"], [data-testid="column"] { min-width: min(100%,260px) !important; flex: 1 1 100% !important; }
    .zl-page-intro { margin-bottom: 1.1rem; } .zl-metric-tile { min-height: 126px; }
    .zl-score-ring { width: 96px; height: 96px; }
}
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation-duration: .01ms !important; animation-delay: 0ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; } }
"""


_USER_CSS = r"""
[data-testid="stSidebar"] { background: #0B1730; border-right: 1px solid rgba(255,255,255,.06); }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #DCE6F7; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: .24rem; }
[data-testid="stSidebar"] [role="radiogroup"] label { min-height: 2.45rem; padding: .42rem .65rem; border-left: 3px solid transparent; border-radius: 0 7px 7px 0; transition: background 160ms ease,border-color 160ms ease,box-shadow 160ms ease; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.07); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { border-left-color: #5EA2FF; background: rgba(37,99,235,.22); box-shadow: inset 8px 0 18px rgba(37,99,235,.08); animation: zl-nav-select 180ms ease-out both; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: #FFF !important; font-weight: 800; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1) !important; }
[data-testid="stSidebar"] .zl-brand-name { color: #FFF; }
[data-testid="stSidebar"] .zl-brand-subtitle { color: #9FB0C9; }
.zl-sidebar-user { display: flex; align-items: center; gap: .72rem; padding: .75rem; margin: .35rem 0 .7rem; border: 1px solid rgba(255,255,255,.09); border-radius: 8px; background: rgba(255,255,255,.045); }
.zl-avatar { width: 36px; height: 36px; flex: 0 0 36px; display: grid; place-items: center; border-radius: 50%; color: #FFF; background: linear-gradient(135deg,#2563EB,#7C3AED); font-weight: 800; }
.zl-sidebar-name { color: #FFF; font-weight: 800; overflow-wrap: anywhere; }
.zl-sidebar-school { color: #9FB0C9; font-size: .74rem; margin-top: .1rem; overflow-wrap: anywhere; }
.zl-sidebar-version { color: #9FB0C9; font-size: .7rem; text-align: center; margin-top: .7rem; }
.zl-hero { position: relative; overflow: hidden; min-height: 190px; padding: 1.8rem 2rem; margin-bottom: 1.35rem; border-radius: 8px; color: #FFF; background: linear-gradient(125deg,#0B1730 0%,#17458B 55%,#6030A9 100%); box-shadow: 0 18px 38px rgba(11,23,48,.2); isolation: isolate; }
.zl-hero::before { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .3; background-image: linear-gradient(rgba(255,255,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px); background-size: 34px 34px; mask-image: linear-gradient(90deg,transparent 25%,black 100%); }
.zl-hero::after { content: ""; position: absolute; width: 300px; height: 300px; right: -70px; top: -90px; z-index: -1; border: 1px solid rgba(255,255,255,.22); transform: rotate(24deg); }
.zl-hero h1 { color: #FFF !important; margin: .15rem 0 .4rem; }
.zl-hero p { color: #D9E6FA !important; max-width: 650px; margin: 0; }
.zl-hero-status { display: inline-flex; align-items: center; gap: .35rem; padding: .2rem .55rem; margin-left: .5rem; border: 1px solid rgba(103,232,249,.35); border-radius: 999px; color: #A5F3FC; background: rgba(8,145,178,.18); font-size: .7rem; vertical-align: middle; }
.zl-hero-status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: #22D3EE; }
.zl-quick-icon { color: var(--zl-brand); width: 38px; height: 38px; display: grid; place-items: center; border-radius: 8px; background: #EEF4FF; margin-bottom: .65rem; }
@keyframes zl-nav-select { from { opacity: .78; transform: translateX(-3px); } to { opacity: 1; transform: translateX(0); } }
"""


_ADMIN_CSS = r"""
[data-testid="stSidebar"] { background: #161126; border-right: 1px solid rgba(255,255,255,.07); }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #DED7F5; }
[data-testid="stSidebar"] a { border-radius: 7px; transition: color 160ms ease, background 160ms ease, border-color 160ms ease, box-shadow 160ms ease; }
[data-testid="stSidebar"] a[aria-current="page"] { color: #FFF; background: rgba(109,40,217,.25); border-left: 3px solid #A78BFA; box-shadow: inset 8px 0 18px rgba(109,40,217,.08); animation: zl-admin-nav-select 180ms ease-out both; }
[data-testid="stSidebar"] .zl-brand-name { color: #FFF; }
[data-testid="stSidebar"] .zl-brand-subtitle { color: #AFA5C8; }
.zl-admin-banner { padding: 1.15rem 1.3rem; margin-bottom: 1.2rem; border-left: 4px solid var(--zl-brand); border-radius: 0 8px 8px 0; background: linear-gradient(90deg,#F3EEFF,#FFF); }
@keyframes zl-admin-nav-select { from { opacity: .84; transform: translateX(-2px); } to { opacity: 1; transform: translateX(0); } }
"""


_AUTH_CSS = r"""
:root { color-scheme: dark; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.stApp {
    min-height: 100vh; color: #F7FAFF; background-color: #071021; isolation: isolate;
}
.stApp::before {
    content: ""; position: fixed; inset: -2%; z-index: -1; pointer-events: none;
    background-image: linear-gradient(100deg,rgba(5,12,27,.78),rgba(7,16,33,.56) 52%,rgba(8,15,31,.8)), linear-gradient(rgba(80,120,190,.09) 1px,transparent 1px), linear-gradient(90deg,rgba(80,120,190,.09) 1px,transparent 1px), __DESKTOP_IMAGE__;
    background-size: cover,42px 42px,42px 42px,cover; background-position: center;
    animation: zl-auth-drift 18s ease-in-out infinite alternate;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1260px; min-height: 100vh; padding: 4.2rem 2rem 3rem; display: flex; flex-direction: column; justify-content: center; }
.stApp p, .stApp label, .stApp [data-testid="stCaptionContainer"] { color: #C7D4E8; }
.stApp h1, .stApp h2, .stApp h3 { color: #FFF; }
.zl-auth-copy, .st-key-auth_copy { max-width: 650px; padding: 2rem 1rem 2rem 0; animation: zl-auth-left 520ms cubic-bezier(.22,1,.36,1) both; }
.zl-auth-kicker { color: #67E8F9; font-size: .74rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.zl-auth-copy h1, .st-key-auth_copy h1 { max-width: 620px; margin: .75rem 0 1rem; color: #FFF !important; font-size: 3.35rem !important; line-height: 1.08 !important; }
.zl-auth-copy p, .st-key-auth_copy p { max-width: 560px; color: #C6D6EC !important; font-size: 1.04rem; line-height: 1.8; }
.zl-auth-proof { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.45rem; }
.zl-auth-proof span { padding: .38rem .65rem; border: 1px solid rgba(139,180,239,.22); border-radius: 999px; color: #D7E7FC; background: rgba(10,28,57,.48); font-size: .76rem; backdrop-filter: blur(8px); }
.st-key-auth_panel { padding: 1.35rem 1.45rem 1.5rem; border: 1px solid rgba(180,205,240,.2); border-radius: 8px; background: rgba(10,22,44,.82); box-shadow: 0 30px 80px rgba(0,0,0,.36),inset 0 1px 0 rgba(255,255,255,.08); backdrop-filter: blur(18px); animation: zl-auth-right 560ms 80ms cubic-bezier(.22,1,.36,1) both; }
.st-key-auth_panel div[data-testid="stForm"] { padding: .65rem 0 0; border: 0 !important; background: transparent; box-shadow: none; }
.st-key-auth_panel [data-testid="stTextInputRootElement"], .st-key-auth_panel [data-testid="stTextAreaRootElement"], .st-key-auth_panel [data-baseweb="select"] > div { color: #F8FAFF !important; background: rgba(4,12,26,.72) !important; border-color: rgba(170,195,230,.3) !important; }
.st-key-auth_panel [data-testid="stTextInput"] input, .st-key-auth_panel [data-testid="stTextArea"] textarea { color: #F8FAFF !important; -webkit-text-fill-color: #F8FAFF !important; }
.st-key-auth_panel [data-testid="stTextInputRootElement"]:focus-within { border-color: #60A5FA !important; box-shadow: 0 0 0 3px rgba(59,130,246,.2) !important; }
.st-key-auth_panel p, .st-key-auth_panel label, .st-key-auth_panel span { color: #DCE8F8; }
.st-key-auth_mode [data-testid="stButtonGroup"] { width: 100%; background: rgba(4,12,26,.6); border: 1px solid rgba(170,195,230,.22); border-radius: 8px; }
.st-key-auth_mode [role="radiogroup"] { width: 100%; }
.st-key-auth_mode button { flex: 1 1 0; width: auto; color: #DCE8F8 !important; background: #101E36 !important; border-radius: 7px; }
.st-key-auth_mode button p { color: inherit !important; }
.st-key-auth_mode button:hover { background: #203555 !important; }
.st-key-auth_mode button[aria-checked="true"] { color: #FFF !important; background: linear-gradient(110deg,#2563EB,#7C3AED) !important; }
.st-key-auth_mode button[aria-checked="true"] p { color: #FFF !important; }
.zl-auth-panel-head { margin: .1rem 0 1rem; }
.zl-auth-panel-head h2 { margin: 0; color: #FFF !important; }
.zl-auth-panel-head p { margin: .35rem 0 0; color: #9FB0C9 !important; font-size: .86rem; }
.zl-auth-foot { margin-top: 1rem; color: #A9BAD2; font-size: .72rem; text-align: center; }
@keyframes zl-auth-left { from { opacity: 0; transform: translateX(-18px); } to { opacity: 1; transform: translateX(0); } }
@keyframes zl-auth-right { from { opacity: 0; transform: translateX(18px); } to { opacity: 1; transform: translateX(0); } }
@keyframes zl-auth-drift { from { transform: translateX(-8px); } to { transform: translateX(8px); } }
@media (max-width: 767px) {
    .stApp::before { background-image: linear-gradient(180deg,rgba(5,12,27,.78),rgba(5,12,27,.95)), linear-gradient(rgba(80,120,190,.07) 1px,transparent 1px), linear-gradient(90deg,rgba(80,120,190,.07) 1px,transparent 1px), __MOBILE_IMAGE__; background-size: cover,34px 34px,34px 34px,cover; }
    .block-container { justify-content: flex-start; padding: 1.2rem .85rem 2rem; }
    .zl-auth-copy, .st-key-auth_copy { padding: .7rem .2rem .45rem; }
    .zl-auth-copy h1, .st-key-auth_copy h1 { font-size: 2rem !important; margin: .45rem 0 .55rem; }
    .zl-auth-copy p, .st-key-auth_copy p, .zl-auth-proof { display: none; }
    .st-key-auth_panel { padding: 1rem; }
}
"""
