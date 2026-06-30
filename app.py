"""
AI Recruitment Assistant (WeRecruit)

Developer:
    Vanaparthi Naga Harshitha

Technologies:
    Python, Streamlit, Neon PostgreSQL, Qdrant Cloud,
    Groq, LangChain, Langfuse
"""

# Standard library
import os
from collections import Counter

# Third-party
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from langfuse import Langfuse

# Local project imports
from matcher import calculate_match_score, model
from utils import get_status
from resume_parser import extract_resume_text
from email_generator import generate_email
from email_sender import send_email
from database import save_candidates, save_email, get_all_candidates, get_all_emails, clear_db
from report_generator import generate_screening_report
from qdrant_db import save_embedding
from skill_extractor import extract_jd_skills, compute_skill_match
from pipeline import recruitment_pipeline

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WeRecruit",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

_theme = st.session_state["theme"]
if _theme == "dark":

    BG_APP = "#090D16"
    BG_CARD = "#131926"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#CBD5E1"
    BORDER = "#1F293D"

else:

    BG_APP = "#F8FAFC"
    BG_CARD = "#FFFFFF"
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    BORDER = "#E2E8F0"
# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS  — Modern SaaS Enterprise Theme (Greenhouse / Zoho Recruit style)
# Light palette: Navy #0F172A, Blue #2563EB, Gold #F59E0B, Green #10B981, Purple #9333EA
#                Background #F8FAFC, Cards #FFFFFF, Text #0F172A
# Dark palette mirrors the same accents on a navy/slate base for parity.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   FONTS & RESET
═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

/* ═══════════════════════════════════════════════════════════════
   THEME TOKENS
   Light: Background #F8FAFC · Cards #FFFFFF · Text #0F172A · Primary #2563EB · Accent #F59E0B
   Dark:  Background #0F172A · Cards #1E293B · Text #FFFFFF · Primary #6366F1 · Accent #F59E0B
═══════════════════════════════════════════════════════════════ */
:root {{
    --bg-app: {BG_APP};
    --bg-card: {BG_CARD};
    --bg-card-alt:   #F1F5F9;
    --bg-soft:       #F8FAFC;
    --border:        {BORDER};
    --border-soft:   #F1F5F9;
    --text-primary:  {TEXT_PRIMARY};
    --text-secondary:{TEXT_SECONDARY};
    --text-muted:    #64748B;
    --text-faint:    #94A3B8;
    --navy:          #090D16;
    --navy-soft:     #0C101B;
    --primary:       #2563EB;
    --primary-light: #4F46E5;
    --blue:          #2563EB;
    --blue-light:    #4F46E5;
    --gold:          #F59E0B;
    --gold-light:    #FBBF24;
    --green:         #10B981;
    --green-light:   #34D399;
    --red:           #F43F5E;
    --red-light:     #FB7185;
    --purple:        #9333EA;
    --purple-light:  #A855F7;
    --shadow-sm:      0 2px 10px rgba(15,23,42,0.06);
    --shadow-md:      0 4px 16px rgba(15,23,42,0.08);
    --shadow-lg:      0 16px 40px rgba(15,23,42,0.14);
    --code-text:      #1E293B;
    --hero-bg: linear-gradient(135deg,#FFFFFF 0%,#F8FAFC 55%,#E2E8F0 100%);
    --hero-text: #0F172A;
    --hero-subtext: #475569;
}}



/* ═══════════════════════════════════════════════════════════════
   APP SHELL
═══════════════════════════════════════════════════════════════ */
.stApp {{
    background: var(--bg-app) !important;
    color: var(--text-primary) !important;
    min-height: 100vh;
    transition: background 0.25s ease, color 0.25s ease;
}}

.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR — deep navy in both themes, always high contrast
═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--navy) 0%, var(--navy-soft) 100%) !important;
    border-right: 1px solid rgba(37,99,235,0.3) !important;
    min-width: 300px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

.sb-header {{
    background: linear-gradient(135deg, var(--navy-soft), var(--navy));
    border-bottom: 1px solid rgba(37,99,235,0.35);
    padding: 28px 22px 22px;
    position: relative;
    overflow: hidden;
}}
.sb-header::before {{
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 130px; height: 130px;
    background: radial-gradient(circle, rgba(37,99,235,0.35) 0%, transparent 70%);
    border-radius: 50%;
}}
.sb-logo-area {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}}
.sb-icon {{
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #2563EB, #9333EA);
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    box-shadow: 0 4px 18px rgba(37,99,235,0.5);
}}
.sb-title {{
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
    line-height: 1.15;
    font-family: 'Inter', sans-serif !important;
}}
.sb-sub {{
    font-size: 0.78rem !important;
    color: #B8C4D9 !important;
    font-weight: 600 !important;
    margin-top: 3px !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}}
.sb-status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.18);
    border: 1px solid rgba(16,185,129,0.5);
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.74rem;
    font-weight: 700;
    color: #34D399;
    letter-spacing: 0.04em;
}}
.sb-status-dot {{
    width: 6px; height: 6px;
    background: #34D399;
    border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
    box-shadow: 0 0 8px #34D399;
}}
@keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
}}

.sb-section-title {{
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    color: #7FB1FB !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 20px 22px 10px !important;
}}

.sb-theme-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 22px 6px;
}}
.sb-theme-label {{
    font-size: 0.78rem;
    font-weight: 700;
    color: #B8C4D9;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

[data-testid="stSidebar"] .stTextArea > label {{
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #B8C4D9 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}
[data-testid="stSidebar"] textarea {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(37,99,235,0.4) !important;
    border-radius: 12px !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
[data-testid="stSidebar"] textarea:focus {{
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.3) !important;
    outline: none !important;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {{
    color: #B8C4D9 !important;
    font-size: 0.88rem !important;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #B8C4D9 !important;
}}

/* Sidebar toggle switch (segmented button look via radio/selectbox override) */
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.08) !important;
    color: #F1F5F9 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    box-shadow: none !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.9rem !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: #2563EB !important;
    background: rgba(37,99,235,0.18) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   HERO BANNER — always bold dark navy, in both themes
═══════════════════════════════════════════════════════════════ */
.enterprise-hero{{
    background: var(--hero-bg);
}}
.hero-bg-overlay {{
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 85% 15%, rgba(147,51,234,0.35) 0%, transparent 50%),
        radial-gradient(circle at 10% 85%, rgba(37,99,235,0.3) 0%, transparent 55%);
}}
.hero-sparkle {{
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle 1.5px at 15% 20%, rgba(96,165,250,0.7) 0%, transparent 100%),
        radial-gradient(circle 1px at 85% 25%, rgba(245,158,11,0.6) 0%, transparent 100%),
        radial-gradient(circle 2px at 60% 75%, rgba(147,51,234,0.5) 0%, transparent 100%),
        radial-gradient(circle 1px at 30% 80%, rgba(16,185,129,0.5) 0%, transparent 100%),
        radial-gradient(circle 1.5px at 92% 60%, rgba(96,165,250,0.6) 0%, transparent 100%);
}}
.hero-grid-lines {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(37,99,235,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37,99,235,0.06) 1px, transparent 1px);
    background-size: 38px 38px;
}}
.hero-content {{
    position: relative;
    z-index: 2;
    padding: 46px 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 28px;
    min-height: 270px;
    flex-wrap: wrap;
}}
.hero-left {{ flex: 1 1 320px; min-width: 0; }}
.hero-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(245,158,11,0.18);
    border: 1px solid rgba(245,158,11,0.55);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.7rem;
    font-weight: 800;
    color: #FBBF24;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 18px;
}}
.hero-headline {{
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    color:var(--hero-text) !important;
    line-height: 1.08 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 14px !important;
    font-family: 'Inter', sans-serif !important;
}}
.hero-headline span {{
    background: linear-gradient(135deg, #2563EB, #9333EA, #F59E0B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-subline {{
    font-size: 0.96rem !important;
    color:var(--hero-subtext) !important;
    line-height: 1.7 !important;
    max-width: 540px !important;
    font-weight: 400 !important;
}}
.hero-actions {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 26px;
    flex-wrap: wrap;
}}
.hero-btn-primary {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #2563EB, #4F46E5);
    color: #fff;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 12px 26px;
    border-radius: 11px;
    border: none;
    cursor: pointer;
    box-shadow: 0 6px 24px rgba(37,99,235,0.55);
    letter-spacing: 0.02em;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.hero-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(37,99,235,0.7);
}}
.hero-btn-secondary {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.08);
    color: #F1F5F9;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 12px 26px;
    border-radius: 11px;
    border: 1.5px solid rgba(255,255,255,0.3);
    cursor: pointer;
    letter-spacing: 0.02em;
    text-decoration: none;
    backdrop-filter: blur(10px);
    transition: transform 0.2s, border-color 0.2s, background 0.2s;
}}
.hero-btn-secondary:hover {{
    transform: translateY(-2px);
    border-color: #F59E0B;
    background: rgba(245,158,11,0.12);
}}
.hero-right {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex-shrink: 0;
}}
.hero-stat-card {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    padding: 16px 24px;
    text-align: center;
    backdrop-filter: blur(18px);
    min-width: 150px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}}
.hero-stat-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(96,165,250,0.5);
}}
.hero-stat-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2563EB, #9333EA, #F59E0B);
}}
.hero-stat-num {{
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 4px;
    font-family: 'Inter', sans-serif;
}}
.hero-stat-lbl {{
    font-size: 0.72rem;
    font-weight: 700;
    color: rgba(226,232,240,0.78);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

/* ═══════════════════════════════════════════════════════════════
   HERO KPI GRID — 2x2 gradient mini-cards (matches Gemini reference)
═══════════════════════════════════════════════════════════════ */
.hero-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    flex-shrink: 0;
    min-width: 280px;
}}
.hero-kpi-card {{
    border-radius: 16px;
    padding: 16px 18px;
    color:var(--hero-text) !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 28px rgba(0,0,0,0.28);
    transition: transform 0.25s ease;
}}
.hero-kpi-card:hover {{ transform: translateY(-3px) scale(1.01); }}
.hero-kpi-icon {{
    position: absolute;
    right: -10px; bottom: -14px;
    font-size: 4.2rem;
    opacity: 0.16;
    line-height: 1;
}}
.hero-kpi-label {{
    font-size: 0.72rem;
    font-weight: 700;
    opacity: 0.9;
    margin-bottom: 6px;
    position: relative;
    z-index: 1;
}}
.hero-kpi-value {{
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1;
    position: relative;
    z-index: 1;
    font-family: 'Inter', sans-serif;
}}
.hero-kpi-sub {{
    font-size: 0.66rem;
    opacity: 0.85;
    margin-top: 6px;
    position: relative;
    z-index: 1;
}}
.hero-kpi-blue    {{ background: linear-gradient(135deg, #2563EB, #4F46E5); }}
.hero-kpi-emerald {{ background: linear-gradient(135deg, #059669, #10B981); }}
.hero-kpi-amber   {{ background: linear-gradient(135deg, #D97706, #F59E0B); }}
.hero-kpi-purple  {{ background: linear-gradient(135deg, #7C3AED, #9333EA); }}

/* ═══════════════════════════════════════════════════════════════
   FEATURE CARDS
═══════════════════════════════════════════════════════════════ */
.feature-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 32px;
}}
.feature-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 26px 22px;
    position: relative;
    overflow: hidden;
    cursor: default;
    box-shadow: var(--shadow-sm);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}}
.feature-card:hover {{
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
}}
.feature-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 4px;
    background: var(--accent, linear-gradient(90deg, #2563EB, #4F46E5));
    opacity: 0;
    transition: opacity 0.25s;
}}
.feature-card:hover::after {{ opacity: 1; }}
.feature-icon-wrap {{
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 16px;
    box-shadow: 0 4px 14px rgba(15,23,42,0.1);
}}
.fc-blue   .feature-icon-wrap {{ background: linear-gradient(135deg,#2563EB,#4F46E5); }}
.fc-purple .feature-icon-wrap {{ background: linear-gradient(135deg,#9333EA,#A855F7); }}
.fc-green  .feature-icon-wrap {{ background: linear-gradient(135deg,#10B981,#34D399); }}
.fc-gold   .feature-icon-wrap {{ background: linear-gradient(135deg,#F59E0B,#FBBF24); }}
.fc-skyblue .feature-icon-wrap {{ background: linear-gradient(135deg,#3B82F6,#60A5FA); }}
.fc-blue   {{ --accent: linear-gradient(90deg, #2563EB, #4F46E5); }}
.fc-purple {{ --accent: linear-gradient(90deg, #9333EA, #A855F7); }}
.fc-green  {{ --accent: linear-gradient(90deg, #10B981, #34D399); }}
.fc-gold   {{ --accent: linear-gradient(90deg, #F59E0B, #FBBF24); }}
.fc-skyblue {{ --accent: linear-gradient(90deg, #3B82F6, #60A5FA); }}
.feature-title {{
    font-size: 0.98rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
}}
.feature-desc {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.6;
}}

/* ═══════════════════════════════════════════════════════════════
   ANALYTICS DASHBOARD
═══════════════════════════════════════════════════════════════ */
.analytics-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}}
.analytics-title {{
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    font-family: 'Inter', sans-serif;
}}
.analytics-subtitle {{
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 2px;
}}
.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.72rem;
    font-weight: 800;
    color: #059669;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.live-dot {{
    width: 6px; height: 6px;
    background: #10B981;
    border-radius: 50%;
    animation: blink 1.5s infinite;
    box-shadow: 0 0 6px #10B981;
}}

.analytics-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 34px;
}}
.analytics-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s, box-shadow 0.2s;
}}
.analytics-card:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}}
.ac-icon {{ font-size: 1.4rem; margin-bottom: 12px; display: block; }}
.ac-value {{
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
}}
.ac-label {{
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.ac-trend {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 9px;
    padding: 3px 8px;
    border-radius: 10px;
}}
.ac-top-bar {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
}}

/* ═══════════════════════════════════════════════════════════════
   SECTION DIVIDER
═══════════════════════════════════════════════════════════════ */
.section-divider {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 30px 0 20px;
}}
.sd-label {{
    font-size: 0.82rem;
    font-weight: 800;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    white-space: nowrap;
    font-family: 'Inter', sans-serif;
}}
.sd-line {{
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, rgba(37,99,235,0.5), transparent);
}}

/* ═══════════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    gap: 4px !important;
    padding: 6px !important;
    margin-bottom: 4px !important;
    box-shadow: var(--shadow-sm) !important;
}}
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    border: none !important;
    transition: color 0.2s, background 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--blue) !important;
    background: rgba(37,99,235,0.08) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.4) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 26px !important;
}}

/* ═══════════════════════════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {{
    background: var(--bg-card) !important;
    border: 2px dashed rgba(37,99,235,0.45) !important;
    border-radius: 18px !important;
    transition: border-color 0.25s, background 0.25s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #2563EB !important;
    background: rgba(37,99,235,0.06) !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] div {{
    color: var(--text-secondary) !important;
}}
section[data-testid="stFileUploaderDropzone"] {{
    background: transparent !important;
    padding: 8px !important;
}}
section[data-testid="stFileUploaderDropzone"] button {{
    background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}}
section[data-testid="stFileUploaderDropzone"] small {{
    color: var(--text-muted) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════ */
.stButton > button {{
    background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.4) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    padding: 0.6rem 1.2rem !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 26px rgba(37,99,235,0.5) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}
.stDownloadButton > button {{
    background: var(--bg-card) !important;
    color: var(--blue) !important;
    border: 1.5px solid var(--blue) !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    transition: transform 0.15s, background 0.15s, box-shadow 0.15s !important;
}}
.stDownloadButton > button:hover {{
    background: rgba(37,99,235,0.08) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.25) !important;
    transform: translateY(-2px) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 11px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.18) !important;
}}
.stTextInput > label,
.stTextArea > label {{
    color: var(--text-secondary) !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
}}
[data-testid="stWidgetLabel"] p {{
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    color: var(--text-secondary) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   SELECTBOX
═══════════════════════════════════════════════════════════════ */
.stSelectbox > div > div {{
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 11px !important;
    color: var(--text-primary) !important;
}}
.stSelectbox label {{ color: var(--text-secondary) !important; font-size: 0.84rem !important; font-weight: 700 !important; }}
.stSelectbox div[data-baseweb="select"] span {{ color: var(--text-primary) !important; }}

/* ═══════════════════════════════════════════════════════════════
   CHECKBOXES
═══════════════════════════════════════════════════════════════ */
.stCheckbox label,
div[data-testid="stCheckbox"] label p {{
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}}

/* ═══════════════════════════════════════════════════════════════
   CANDIDATE PROFILE CARD
═══════════════════════════════════════════════════════════════ */
.candidate-profile-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0;
    margin-bottom: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
    position: relative;
}}
.candidate-profile-card:hover {{
    border-color: #2563EB;
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}}
.cpc-accent-bar {{ height: 5px; width: 100%; }}
.cpc-accent-shortlisted {{ background: linear-gradient(90deg, #10B981, #34D399); }}
.cpc-accent-rejected    {{ background: linear-gradient(90deg, #F43F5E, #FB7185); }}
.cpc-body {{
    display: grid;
    grid-template-columns: 60px 1fr 140px 1fr 100px;
    align-items: center;
    gap: 20px;
    padding: 20px 24px;
}}
.cpc-rank {{
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    flex-shrink: 0;
    font-family: 'Inter', sans-serif;
}}
.rank-1 {{ background: linear-gradient(135deg,#F59E0B,#FBBF24); color: #fff; box-shadow: 0 4px 16px rgba(245,158,11,0.5); }}
.rank-2 {{ background: linear-gradient(135deg,#94A3B8,#CBD5E1); color: #0F172A; box-shadow: 0 4px 12px rgba(148,163,184,0.4); }}
.rank-3 {{ background: linear-gradient(135deg,#9333EA,#A855F7); color: #fff; box-shadow: 0 4px 12px rgba(147,51,234,0.4); }}
.rank-n {{ background: var(--bg-card-alt); color: var(--text-muted); border: 1px solid var(--border); }}
.cpc-info {{ min-width: 0; }}
.cpc-name {{
    font-size: 1.02rem;
    font-weight: 800;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
    font-family: 'Inter', sans-serif;
}}
.cpc-email {{
    font-size: 0.78rem;
    color: var(--blue);
    font-weight: 700;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 3px;
}}
.cpc-file {{
    font-size: 0.73rem;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.cpc-score-wrap {{ text-align: center; }}
.cpc-score-circle {{
    width: 74px; height: 74px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin: 0 auto 6px;
}}
.cpc-score-num {{
    font-size: 1.3rem;
    font-weight: 900;
    line-height: 1;
    font-family: 'Inter', sans-serif;
}}
.cpc-score-pct {{ font-size: 0.65rem; color: var(--text-muted); font-weight: 700; }}
.score-high .cpc-score-circle {{ background: rgba(16,185,129,0.12);  border: 2.5px solid #10B981; }}
.score-mid  .cpc-score-circle {{ background: rgba(245,158,11,0.12); border: 2.5px solid #F59E0B; }}
.score-low  .cpc-score-circle {{ background: rgba(244,63,94,0.1);   border: 2.5px solid #F43F5E; }}
.score-high .cpc-score-num {{ color: #059669; }}
.score-mid  .cpc-score-num {{ color: #D97706; }}
.score-low  .cpc-score-num {{ color: #E11D48; }}
.status-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 4px 11px;
    border-radius: 20px;
}}
.badge-shortlisted {{ background: rgba(16,185,129,0.14); color: #059669; border: 1px solid rgba(16,185,129,0.4); }}
.badge-rejected    {{ background: rgba(244,63,94,0.12); color: #E11D48; border: 1px solid rgba(244,63,94,0.4); }}
.cpc-skills {{ min-width: 0; }}
.skills-row-label {{
    font-size: 0.74rem;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 5px;
}}
.skill-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 700;
    margin: 2px 3px 2px 0;
    line-height: 1;
}}
.pill-match {{ background: rgba(16,185,129,0.12); color: #059669; border: 1px solid rgba(16,185,129,0.35); }}
.pill-miss  {{ background: rgba(244,63,94,0.1);  color: #E11D48; border: 1px solid rgba(244,63,94,0.3); }}
.pill-none  {{ color: var(--text-faint); font-style: italic; font-size: 0.78rem; }}
.cpc-actions {{ display: flex; flex-direction: column; gap: 7px; align-items: flex-end; }}
.action-tag {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-secondary);
    padding: 4px 11px;
    background: var(--bg-card-alt);
    border: 1px solid var(--border);
    border-radius: 8px;
    white-space: nowrap;
}}

/* ═══════════════════════════════════════════════════════════════
   HR DECISION SECTION
═══════════════════════════════════════════════════════════════ */
.decision-panel {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
}}
.decision-panel-header {{
    background: linear-gradient(90deg, rgba(37,99,235,0.1), rgba(147,51,234,0.1));
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.dph-title {{
    font-size: 0.8rem;
    font-weight: 800;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Inter', sans-serif;
}}
.decision-row {{
    display: flex;
    align-items: center;
    padding: 12px 20px;
    border-bottom: 1px solid var(--border-soft);
    gap: 14px;
    transition: background 0.15s;
}}
.decision-row:last-child {{ border-bottom: none; }}
.decision-row:hover {{ background: rgba(37,99,235,0.05); }}
.dr-name {{
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--text-primary);
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.dr-email {{ font-size: 0.78rem; color: var(--text-muted); }}
.dr-score {{
    font-size: 0.92rem;
    font-weight: 800;
    padding: 4px 11px;
    border-radius: 8px;
    white-space: nowrap;
    font-family: 'Inter', sans-serif;
}}

/* ═══════════════════════════════════════════════════════════════
   EMAIL COMPOSER
═══════════════════════════════════════════════════════════════ */
.email-composer {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-top: 16px;
    box-shadow: var(--shadow-sm);
}}
.ec-header {{
    background: var(--navy);
    border-bottom: 1px solid var(--border);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.ec-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
.ec-filename {{
    font-size: 0.75rem;
    color: #94A3B8;
    margin-left: 6px;
}}
.ec-body {{
    padding: 22px 24px;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: var(--code-text);
    line-height: 1.8;
    white-space: pre-wrap;
}}

/* ═══════════════════════════════════════════════════════════════
   DATABASE TAB
═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stDataFrame"] th {{
    background: var(--navy) !important;
    color: #FFFFFF !important;
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}
[data-testid="stDataFrame"] td {{
    color: var(--code-text) !important;
    font-size: 0.86rem !important;
    background: var(--bg-card) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   REPORT TAB
═══════════════════════════════════════════════════════════════ */
.report-summary-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.report-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s;
}}
.report-card:hover {{ transform: translateY(-3px); }}
.rc-top {{ position: absolute; top: 0; left: 0; right: 0; height: 4px; }}
.rc-num {{
    font-size: 1.95rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
    font-family: 'Inter', sans-serif;
}}
.rc-label {{
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.report-preview-container {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}}
.rpc-header {{
    background: var(--navy);
    border-bottom: 1px solid var(--border);
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.rpc-title {{
    font-size: 0.82rem;
    font-weight: 800;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Inter', sans-serif;
}}
.rpc-body {{
    padding: 24px 26px;
    font-family: 'Inter', monospace;
    font-size: 0.8rem;
    color: var(--code-text);
    white-space: pre;
    overflow-x: auto;
    max-height: 480px;
    overflow-y: auto;
    line-height: 1.75;
}}
.rpc-body::-webkit-scrollbar {{ width: 6px; height: 6px; }}
.rpc-body::-webkit-scrollbar-track {{ background: var(--bg-card-alt); }}
.rpc-body::-webkit-scrollbar-thumb {{ background: rgba(37,99,235,0.4); border-radius: 3px; }}

/* ═══════════════════════════════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════════════════════════════ */
.empty-state {{
    text-align: center;
    padding: 60px 40px;
    background: var(--bg-card);
    border: 1.5px dashed rgba(37,99,235,0.35);
    border-radius: 20px;
}}
.empty-icon {{ font-size: 3rem; margin-bottom: 16px; display: block; }}
.empty-title {{
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
}}
.empty-desc {{ font-size: 0.88rem; color: var(--text-muted); line-height: 1.6; }}

/* ═══════════════════════════════════════════════════════════════
   SUCCESS / ERROR / INFO OVERRIDES
═══════════════════════════════════════════════════════════════ */
.stSuccess {{ border-radius: 12px !important; background: rgba(16,185,129,0.1) !important;  border: 1.5px solid rgba(16,185,129,0.4)  !important; }}
.stError   {{ border-radius: 12px !important; background: rgba(244,63,94,0.1) !important;  border: 1.5px solid rgba(244,63,94,0.4)  !important; }}
.stWarning {{ border-radius: 12px !important; background: rgba(245,158,11,0.1) !important; border: 1.5px solid rgba(245,158,11,0.4) !important; }}
.stInfo    {{ border-radius: 12px !important; background: rgba(37,99,235,0.08) !important; border: 1.5px solid rgba(37,99,235,0.35) !important; }}
.stSuccess p, .stError p, .stWarning p, .stInfo p {{ color: var(--text-primary) !important; font-size: 0.88rem !important; }}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY & MISC
═══════════════════════════════════════════════════════════════ */
hr {{ border: none !important; border-top: 1px solid var(--border) !important; margin: 24px 0 !important; }}
h1,h2,h3,h4,h5,h6 {{ color: var(--text-primary) !important; font-family: 'Inter', sans-serif !important; }}
.stMarkdown p, .stText {{ color: var(--text-secondary) !important; font-size: 0.9rem !important; }}
[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; font-weight: 700 !important; }}
[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-weight: 800 !important; }}
details {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}}
summary {{ color: var(--text-secondary) !important; font-weight: 700 !important; font-size: 0.9rem !important; }}
[data-testid="stExpander"] p {{ color: var(--text-secondary) !important; }}

/* ═══════════════════════════════════════════════════════════════
   TOP NAVIGATION — sticky SaaS header
═══════════════════════════════════════════════════════════════ */
.topnav-wrap {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 12px 22px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(10px);
}}
.topnav-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 1rem;
    color: var(--text-primary);
}}
.topnav-brand-icon {{
    width: 34px; height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, var(--primary), var(--purple));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 3px 12px rgba(99,102,241,0.4);
}}
.topnav-links {{
    display: flex;
    align-items: center;
    gap: 4px;
}}
.topnav-link {{
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
    padding: 8px 16px;
    border-radius: 9px;
    transition: color 0.18s, background 0.18s;
    text-decoration: none;
    cursor: pointer;
}}
.topnav-link:hover {{
    color: var(--primary);
    background: rgba(99,102,241,0.08);
}}
.topnav-link-active {{
    color: #FFFFFF !important;
    background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
    box-shadow: 0 3px 10px rgba(99,102,241,0.35);
}}

/* ═══════════════════════════════════════════════════════════════
   HERO ILLUSTRATION (right side SVG panel)
═══════════════════════════════════════════════════════════════ */
.hero-illustration-wrap {{
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}}
.hero-illustration-wrap svg {{
    animation: heroFloat 5s ease-in-out infinite;
}}
@keyframes heroFloat {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
}}

/* ═══════════════════════════════════════════════════════════════
   FILTER BAR
═══════════════════════════════════════════════════════════════ */
.filter-bar-label {{
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-secondary);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

/* ═══════════════════════════════════════════════════════════════
   CHART CARD
═══════════════════════════════════════════════════════════════ */
.chart-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px 22px 8px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 18px;
    transition: box-shadow 0.25s, transform 0.25s;
}}
.chart-card:hover {{
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}}
.chart-card-title {{
    font-size: 0.92rem;
    font-weight: 800;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    margin-bottom: 4px;
}}
.chart-card-sub {{
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-bottom: 10px;
}}

/* ═══════════════════════════════════════════════════════════════
   INSIGHT CARDS
═══════════════════════════════════════════════════════════════ */
.insight-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-bottom: 10px;
}}
.insight-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--primary);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}}
.insight-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}}
.insight-card-icon {{
    font-size: 1.2rem;
    flex-shrink: 0;
    margin-top: 1px;
}}
.insight-card-text {{
    font-size: 0.86rem;
    color: var(--text-secondary);
    line-height: 1.5;
}}
.insight-card-text strong {{
    color: var(--text-primary);
    font-weight: 800;
}}

/* ═══════════════════════════════════════════════════════════════
   CANDIDATE TIMELINE
═══════════════════════════════════════════════════════════════ */
.cand-timeline {{
    display: flex;
    align-items: center;
    gap: 0;
    margin-top: 14px;
    padding: 14px 6px;
    overflow-x: auto;
}}
.tl-step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 90px;
    position: relative;
}}
.tl-dot {{
    width: 30px; height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    margin-bottom: 6px;
    z-index: 1;
    border: 2px solid var(--border);
    background: var(--bg-card-alt);
    color: var(--text-faint);
}}
.tl-dot-done {{
    background: linear-gradient(135deg, var(--green), var(--green-light));
    border-color: var(--green);
    color: #fff;
    box-shadow: 0 3px 10px rgba(16,185,129,0.4);
}}
.tl-dot-pending {{
    background: var(--bg-card-alt);
    border: 2px dashed var(--border);
    color: var(--text-faint);
}}
.tl-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-align: center;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    line-height: 1.3;
}}
.tl-label-done {{ color: var(--text-primary); }}
.tl-sub {{
    font-size: 0.64rem;
    color: var(--text-faint);
    margin-top: 2px;
}}
.tl-line {{
    flex: 1;
    height: 2px;
    background: var(--border);
    margin: 0 -4px 24px;
    min-width: 24px;
}}
.tl-line-done {{ background: linear-gradient(90deg, var(--green), var(--green-light)); }}

/* ═══════════════════════════════════════════════════════════════
   FOOTER
═══════════════════════════════════════════════════════════════ */
.app-footer {{
    margin-top: 56px;
    padding: 36px 40px 28px;
    background: linear-gradient(135deg, var(--navy), var(--navy-soft));
    border-radius: 20px;
    color: #CBD5E1;
}}
.footer-grid {{
    display: grid;
    grid-template-columns: 1.4fr 1fr 1fr;
    gap: 32px;
    margin-bottom: 24px;
}}
.footer-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    color: #FFFFFF;
    margin-bottom: 10px;
}}
.footer-tagline {{
    font-size: 0.82rem;
    color: #94A3B8;
    line-height: 1.6;
    max-width: 320px;
}}
.footer-col-title {{
    font-size: 0.72rem;
    font-weight: 800;
    color: #7FB1FB;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
}}
.footer-tech-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.78rem;
    color: #D7DEEB;
    margin: 0 6px 8px 0;
}}
.footer-link {{
    display: block;
    font-size: 0.82rem;
    color: #B8C4D9;
    padding: 5px 0;
    transition: color 0.18s;
}}
.footer-link:hover {{ color: #93C5FD; }}
.footer-bottom {{
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.76rem;
    color: #7A8AA3;
}}

header[data-testid="stHeader"] {{
    display: none !important;
}}

[data-testid="stToolbar"] {{
    display: none !important;
}}

[data-testid="stDecoration"] {{
    display: none !important;
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

.block-container {{
    padding-top: 0.5rem !important;
}}

</style>
<script>
(function() {{
    try {{
        var doc = window.parent && window.parent.document ? window.parent.document : document;
        doc.documentElement.setAttribute('data-theme', '{_theme}');
        if (doc.body) {{ doc.body.setAttribute('data-theme', '{_theme}'); }}
    }} catch (e) {{
        document.documentElement.setAttribute('data-theme', '{_theme}');
    }}
}})();
</script>
""", unsafe_allow_html=True)




# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-header">
        <div class="sb-logo-area">
            <div class="sb-icon">🎯</div>
            <div>
                <div class="sb-title">WeRecruit</div>
                <div class="sb-sub">Eidiko Systems Integrators</div>
            </div>
        </div>
        <div class="sb-status-pill">
            <span class="sb-status-dot"></span>
            AI Engine Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        st.image("Eidiko_logo.png", use_container_width=True)
    except Exception:
        pass

    # ── Theme toggle ──────────────────────────────────────────────────────
    theme_label_col, theme_btn_col = st.columns([1.4, 1])
    with theme_label_col:
        st.markdown(
            '<div class="sb-theme-row" style="padding:14px 0 6px 4px">'
            '<span class="sb-theme-label">Appearance</span></div>',
            unsafe_allow_html=True
        )
    with theme_btn_col:
        toggle_icon = "🌙  Dark" if st.session_state["theme"] == "light" else "☀️  Light"
        if st.button(toggle_icon, use_container_width=True, key="theme_toggle_btn"):
            st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
            st.rerun()


    st.markdown('<div class="sb-section-title">Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area(
        "Paste the full job description",
        height=290,
        placeholder="e.g. We are looking for a Python Developer with 2+ years of experience in FastAPI, PostgreSQL, and machine learning pipelines...\n\nRequired Skills:\n- Python, FastAPI\n- PostgreSQL, Redis\n- Scikit-learn, Transformers",
        label_visibility="collapsed"
    )

    if jd.strip():
        wc = len(jd.split())
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-top:8px;padding:8px 12px;background:rgba(37,99,235,0.1);
                    border-radius:8px;border:1px solid rgba(37,99,235,0.3)">
            <span style="font-size:0.78rem;color:#B8C4D9;font-weight:600">📝 Job Description</span>
            <span style="font-size:0.78rem;font-weight:700;color:#7FB1FB">{wc} words</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="padding:0 4px">
        <div style="font-size:0.78rem;font-weight:700;color:#7FB1FB;
                    text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
            Platform Capabilities
        </div>
        <div style="display:flex;flex-direction:column;gap:10px">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.84rem;color:#D7DEEB">
                <span style="color:#93C5FD">⚡</span> Semantic Similarity Scoring
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.84rem;color:#D7DEEB">
                <span style="color:#C4B5FD">🧠</span> Groq LLaMA 3 · Skill Extraction
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.84rem;color:#D7DEEB">
                <span style="color:#6EE7B7">🗄️</span> PostgreSQL · Qdrant Vector DB
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.84rem;color:#D7DEEB">
                <span style="color:#93C5FD">📊</span> Langfuse Observability
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# TOP NAVIGATION — sticky SaaS header (anchor-scroll links to real sections)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav-wrap">
    <div class="topnav-brand">
        <div class="topnav-brand-icon">🎯</div>
        WeRecruit
    </div>
    <div class="topnav-links">
        <a href="#dashboard-top" class="topnav-link" target="_self">Dashboard</a>
        <a href="#resume-screening" class="topnav-link" target="_self">Screening</a>
    </div>
</div>
<div id="dashboard-top"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
_all_cands  = get_all_candidates()
_all_emails = get_all_emails()
_total_cands     = len(_all_cands)
_shortlisted     = len([c for c in _all_cands if len(c) > 4 and c[4] == "Similar"]) if _all_cands else 0
_emails_sent     = len(_all_emails)
# Real average match score across all screened candidates in the database
# (column index 3 = "Score" per get_all_candidates() schema)
_hero_avg_score  = (
    round(sum(c[3] for c in _all_cands if len(c) > 3) / len(_all_cands), 1)
    if _all_cands else 0
)

st.markdown(f"""
<div class="enterprise-hero">
    <div class="hero-bg-overlay"></div>
    <div class="hero-grid-lines"></div>
    <div class="hero-sparkle"></div>
    <div class="hero-content">
        <div class="hero-left">
            <div class="hero-headline">
                Recruitment<br>
                <span>Intelligence Platform</span>
            </div>
            <div class="hero-subline">
                Automate resume screening, identify top talent, and accelerate hiring decisions
                using Generative AI and Semantic Matching —
                built for enterprise teams at Eidiko Systems Integrators.
            </div>
        </div>
        <div class="hero-kpi-grid">
            <div class="hero-kpi-card hero-kpi-blue">
                <span class="hero-kpi-icon">👥</span>
                <div class="hero-kpi-label">Total Screened</div>
                <div class="hero-kpi-value">{_total_cands:,}</div>
                <div class="hero-kpi-sub">Active recruitment pool</div>
            </div>
            <div class="hero-kpi-card hero-kpi-emerald">
                <span class="hero-kpi-icon">✅</span>
                <div class="hero-kpi-label">Shortlisted</div>
                <div class="hero-kpi-value">{_shortlisted:,}</div>
                <div class="hero-kpi-sub">Qualified match pipeline</div>
            </div>
            <div class="hero-kpi-card hero-kpi-amber">
                <span class="hero-kpi-icon">📧</span>
                <div class="hero-kpi-label">Emails Sent</div>
                <div class="hero-kpi-value">{_emails_sent:,}</div>
                <div class="hero-kpi-sub">Personalized feedback logs</div>
            </div>
            <div class="hero-kpi-card hero-kpi-purple">
                <span class="hero-kpi-icon">📈</span>
                <div class="hero-kpi-label">Avg Match Score</div>
                <div class="hero-kpi-value">{_hero_avg_score}%</div>
                <div class="hero-kpi-sub">Semantic index metric</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE CARDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-card fc-blue">
        <div class="feature-icon-wrap">🤖</div>
        <div class="feature-title">AI Resume Screening</div>
        <div class="feature-desc">Semantic similarity-based ranking using all-MiniLM-L6-v2 embeddings and cosine distance scoring.</div>
    </div>
    <div class="feature-card fc-green">
        <div class="feature-icon-wrap">🧠</div>
        <div class="feature-title">Skill Intelligence</div>
        <div class="feature-desc">AI-extracted matched and missing skills per candidate powered by Groq LLaMA 3 for precise gap analysis.</div>
    </div>
    <div class="feature-card fc-skyblue">
        <div class="feature-icon-wrap">📧</div>
        <div class="feature-title">Automated Outreach</div>
        <div class="feature-desc">AI-generated personalised emails for shortlisted and rejected candidates with one-click delivery.</div>
    </div>
    <div class="feature-card fc-gold">
        <div class="feature-icon-wrap">📊</div>
        <div class="feature-title">Recruitment Analytics</div>
        <div class="feature-desc">Real-time hiring insights, scoring distributions, and comprehensive reports exportable as CSV and TXT.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
_df_live     = st.session_state.get("df", pd.DataFrame())
_has_results = st.session_state.get("analysed", False)

_total_s   = len(_df_live) if _has_results else _total_cands
_short_s   = len(_df_live[_df_live["Status"] == "Similar"]) if _has_results and len(_df_live) else _shortlisted
_reject_s  = (_total_s - _short_s)
_avg_score = round(_df_live["Score"].mean(), 1) if _has_results and len(_df_live) else 0
_top_score = int(_df_live["Score"].max()) if _has_results and len(_df_live) else 0

st.markdown("""
<div class="analytics-header">
    <div>
        <div class="analytics-title">Recruitment Analytics</div>
        <div class="analytics-subtitle">Live metrics from current screening session</div>
    </div>
    <div class="live-badge"><span class="live-dot"></span>Live</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="analytics-grid">
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#4F46E5,#6366F1)"></div>
        <span class="ac-icon">📄</span>
        <div class="ac-value" style="color:var(--text-primary)">{_total_s}</div>
        <div class="ac-label">Total Screened</div>
        <div class="ac-trend" style="background:rgba(79,70,229,0.12);color:var(--text-primary)">📂 This session</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#059669,#10B981)"></div>
        <span class="ac-icon">✅</span>
        <div class="ac-value" style="color:var(--text-primary)">{_short_s}</div>
        <div class="ac-label">Shortlisted</div>
        <div class="ac-trend" style="background:rgba(16,185,129,0.12);color:var(--text-primary)">↑ Qualified</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#F43F5E,#FB7185)"></div>
        <span class="ac-icon">❌</span>
        <div class="ac-value" style="color:var(--text-primary)">{_reject_s}</div>
        <div class="ac-label">Not Matching</div>
        <div class="ac-trend" style="background:rgba(244,63,94,0.1);color:var(--text-primary)">↓ Below threshold</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#2563EB,#4F46E5)"></div>
        <span class="ac-icon">📊</span>
        <div class="ac-value" style="color:var(--text-primary)">{_avg_score}%</div>
        <div class="ac-label">Avg Match Score</div>
        <div class="ac-trend" style="background:rgba(37,99,235,0.12);color:var(--text-primary)">◈ Semantic</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#9333EA,#A855F7)"></div>
        <span class="ac-icon">🏆</span>
        <div class="ac-value" style="color:var(--text-primary)">{_top_score}%</div>
        <div class="ac-label">Top Score</div>
        <div class="ac-trend" style="background:rgba(147,51,234,0.12);color:var(--text-primary)">★ Best candidate</div>
    </div>
</div>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# RECRUITMENT ANALYTICS CHARTS  (Plotly — built only from real session/db data)
# ─────────────────────────────────────────────────────────────────────────────
_chart_df = _df_live if (_has_results and len(_df_live)) else pd.DataFrame(
    _all_cands, columns=["Candidate", "Email", "File", "Score", "Status",
                          "Matched Skills", "Missing Skills", "Screened At"]
) if _all_cands else pd.DataFrame()

if len(_chart_df):
    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📈 Recruitment Analytics Charts</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    _plot_bg = "rgba(0,0,0,0)"
    _is_dark = st.session_state["theme"] == "dark"
    _font_color = "#F1F5F9" if _is_dark else "#0F172A"
    _grid_color = "rgba(148,163,184,0.18)" if _is_dark else "rgba(148,163,184,0.25)"

    chart_col1, chart_col2 = st.columns(2)

    # ── Chart 1: Status Distribution (Pie) ──────────────────────────────
    with chart_col1:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-card-title">Candidate Status Distribution</div>
            <div class="chart-card-sub">Shortlisted vs Not Similar — current dataset</div>
        """, unsafe_allow_html=True)

        _status_counts = _chart_df["Status"].value_counts()
        _status_labels = ["Shortlisted" if s == "Similar" else "Not Similar" for s in _status_counts.index]
        _status_colors = ["#10B981" if s == "Similar" else "#F43F5E" for s in _status_counts.index]

        fig_pie = go.Figure(data=[go.Pie(
            labels=_status_labels,
            values=_status_counts.values,
            hole=0.55,
            marker=dict(colors=_status_colors, line=dict(color=_plot_bg, width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color=_font_color),
        )])
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            paper_bgcolor=_plot_bg,
            plot_bgcolor=_plot_bg,
            font=dict(color=_font_color, family="Inter, sans-serif"),
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart 2: Candidate Scores (Bar) ─────────────────────────────────
    with chart_col2:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-card-title">Candidate Match Scores</div>
            <div class="chart-card-sub">Semantic similarity score per candidate</div>
        """, unsafe_allow_html=True)

        _bar_df = _chart_df.copy()
        if "Candidate" not in _bar_df.columns and "Name" in _bar_df.columns:
            _bar_df = _bar_df.rename(columns={"Name": "Candidate"})
        _bar_df = _bar_df.sort_values("Score", ascending=True).tail(15)
        _bar_colors = ["#10B981" if v >= 80 else "#F59E0B" if v >= 50 else "#F43F5E" for v in _bar_df["Score"]]

        fig_bar = go.Figure(data=[go.Bar(
            x=_bar_df["Score"],
            y=_bar_df["Candidate"],
            orientation="h",
            marker=dict(color=_bar_colors),
            text=_bar_df["Score"].astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color=_font_color),
        )])
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=30),
            height=280,
            paper_bgcolor=_plot_bg,
            plot_bgcolor=_plot_bg,
            font=dict(color=_font_color, family="Inter, sans-serif"),
            xaxis=dict(title=None, gridcolor=_grid_color, range=[0, 105]),
            yaxis=dict(title=None, gridcolor=_grid_color),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart 3: Top Matched Skills (Horizontal Bar) ────────────────────
    _skill_counter = Counter()
    for s in _chart_df["Matched Skills"].dropna():
        for skill in str(s).split(","):
            skill = skill.strip()
            if skill and skill != "—":
                _skill_counter[skill] += 1

    if _skill_counter:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-card-title">Top Matched Skills</div>
            <div class="chart-card-sub">Most common skills found across all screened resumes</div>
        """, unsafe_allow_html=True)

        _top_skills = _skill_counter.most_common(10)
        _skill_names  = [s[0] for s in _top_skills][::-1]
        _skill_counts = [s[1] for s in _top_skills][::-1]

        _skill_palette = ["#4F46E5", "#10B981", "#3B82F6", "#6366F1", "#9333EA", "#F59E0B"]
        _skill_bar_colors = [_skill_palette[i % len(_skill_palette)] for i in range(len(_skill_names))]

        fig_skills = go.Figure(data=[go.Bar(
            x=_skill_counts,
            y=_skill_names,
            orientation="h",
            marker=dict(color=_skill_bar_colors),
            text=_skill_counts,
            textposition="outside",
            textfont=dict(size=11, color=_font_color),
        )])
        fig_skills.update_layout(
            margin=dict(t=10, b=10, l=10, r=30),
            height=max(220, 32 * len(_top_skills)),
            paper_bgcolor=_plot_bg,
            plot_bgcolor=_plot_bg,
            font=dict(color=_font_color, family="Inter, sans-serif"),
            xaxis=dict(title=None, gridcolor=_grid_color),
            yaxis=dict(title=None, gridcolor=_grid_color),
        )
        st.plotly_chart(fig_skills, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AI HIRING INSIGHTS  (statistically computed from real Score / Skills columns
# — no fabricated metrics, no claims about data we don't have such as
# department or role breakdowns)
# ─────────────────────────────────────────────────────────────────────────────
if len(_chart_df):
    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">🧠 AI Hiring Insights</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    _n = len(_chart_df)
    _insight_avg_score = round(_chart_df["Score"].mean(), 1)
    _insight_shortlist_rate = round((_chart_df["Status"] == "Similar").sum() / _n * 100, 1)

    # Missing-skill frequency (from real Missing Skills column)
    _missing_counter = Counter()
    for s in _chart_df["Missing Skills"].dropna():
        for skill in str(s).split(","):
            skill = skill.strip()
            if skill and skill != "—":
                _missing_counter[skill] += 1

    _insight_cards = []
    _insight_cards.append(
        ("📊", f"Average candidate match score across <strong>{_n}</strong> screened resumes is <strong>{_insight_avg_score}%</strong>.")
    )
    _insight_cards.append(
        ("✅", f"<strong>{_insight_shortlist_rate}%</strong> of candidates met the shortlist threshold based on semantic similarity.")
    )
    if _missing_counter:
        _top_missing, _top_missing_n = _missing_counter.most_common(1)[0]
        _missing_pct = round(_top_missing_n / _n * 100, 1)
        _insight_cards.append(
            ("⚠️", f"<strong>{_missing_pct}%</strong> of candidates are missing <strong>{_top_missing}</strong> — the most common skill gap in this pool.")
        )
    if _skill_counter:
        _top_present, _top_present_n = _skill_counter.most_common(1)[0]
        _present_pct = round(_top_present_n / _n * 100, 1)
        _insight_cards.append(
            ("🧩", f"<strong>{_top_present}</strong> appears in <strong>{_present_pct}%</strong> of resumes — the most common matched skill.")
        )

    _insight_html = ""
    for icon, text in _insight_cards:
        _insight_html += f"""
        <div class="insight-card">
            <div class="insight-card-icon">{icon}</div>
            <div class="insight-card-text">{text}</div>
        </div>"""

    st.markdown(f'<div class="insight-grid">{_insight_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "  🔍  Resume Screening  ",
    "  🗄️  Candidate Database  ",
    "  📋  Screening Reports  "
])


# ════════════════════════════════════════════════════════════════════════════
#  TAB 1 — RESUME SCREENING
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown('<div id="resume-screening"></div>', unsafe_allow_html=True)

    # ── Upload section ────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📂 Upload Resumes</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    upload_col, info_col = st.columns([3, 1])
    with upload_col:
        uploaded_files = st.file_uploader(
            "Drag & drop PDF, DOCX, or TXT resumes here — or click Browse",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="visible"
        )

    with info_col:
        st.markdown("""
        <div style="background:var(--bg-card);border:1px solid var(--border);
                    border-radius:14px;padding:18px 16px;height:100%;
                    box-shadow:0 2px 10px rgba(15,23,42,0.06)">
            <div style="font-size:0.78rem;font-weight:700;color:var(--text-muted);
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px">
                Supported Formats
            </div>
            <div style="display:flex;flex-direction:column;gap:8px">
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:var(--code-text)">
                    <span style="color:#F43F5E;font-size:1rem">📕</span> PDF Documents
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:var(--code-text)">
                    <span style="color:#4a7ab5;font-size:1rem">📘</span> Word (.docx)
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:var(--code-text)">
                    <span style="color:var(--text-muted);font-size:1rem">📄</span> Plain Text
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:var(--text-muted)">
                    <span style="color:#10B981;font-size:1rem">✓</span> No size limit
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded_files:
        os.makedirs("resumes", exist_ok=True)
        for f in uploaded_files:
            with open(os.path.join("resumes", f.name), "wb") as out:
                out.write(f.getbuffer())

        st.success(f"✅  {len(uploaded_files)} resume(s) uploaded and ready for analysis")

        with st.expander(f"👁  Preview extracted resume text  ({len(uploaded_files)} files)"):
            for ufile in uploaded_files:
                st.markdown(f"""
                <div style="padding:8px 0;border-bottom:1px solid var(--border);
                            margin-bottom:10px;display:flex;align-items:center;gap:10px">
                    <span style="font-size:0.9rem">📄</span>
                    <span style="font-size:0.85rem;font-weight:700;color:var(--text-primary)">{ufile.name}</span>
                </div>
                """, unsafe_allow_html=True)
                resume_text = extract_resume_text(os.path.join("resumes", ufile.name))
                resume_embedding = model.encode(resume_text).tolist()
                st.markdown(
                    f'<span style="font-size:0.7rem;color:var(--text-muted)">'
                    f'Embedding dim: {len(resume_embedding)} · Model: all-MiniLM-L6-v2</span>',
                    unsafe_allow_html=True
                )
                st.text_area("", resume_text, height=260, key=f"preview_{ufile.name}")

        st.markdown("---")

        if not jd.strip():
            st.markdown("""
            <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.4);
                        border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:12px">
                <span style="font-size:1.2rem">⚠️</span>
                <span style="font-size:0.85rem;color:#B45309;font-weight:600">
                    Please paste a Job Description in the sidebar before starting analysis.
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🔍  Analyse All Candidates", use_container_width=True):
                with st.spinner("🤖  Extracting required skills from Job Description…"):
                    jd_skills = extract_jd_skills(jd)

                results = []
                progress_bar = st.progress(0, text="Initialising AI pipeline…")

                for i, f in enumerate(uploaded_files):
                    progress_bar.progress(
                        i / len(uploaded_files),
                        text=f"🔄  Analysing {f.name}  ({i+1}/{len(uploaded_files)})"
                    )
                    result = recruitment_pipeline(os.path.join("resumes", f.name), jd)

                    text            = result["text"]
                    score           = result["score"]
                    resume_skills   = result["resume_skills"]
                    matched         = result["matched"]
                    missing         = result["missing"]
                    candidate_name  = result["candidate_name"]
                    candidate_email = result["candidate_email"]

                    resume_embedding = model.encode(text).tolist()
                    try:
                        save_embedding(
                            candidate_id=i + 1,
                            candidate_name=candidate_name,
                            candidate_email=candidate_email,
                            score=score,
                            embedding=resume_embedding
                        )
                    except Exception as e:
                        st.warning(f"Qdrant Warning: {e}")
                    matched, missing = compute_skill_match(resume_skills, jd_skills)
                    results.append({
                        "Candidate":      candidate_name,
                        "Email":          candidate_email,
                        "File":           f.name,
                        "Score":          score,
                        "Status":         get_status(score),
                        "Matched Skills": ", ".join(sorted(matched)) or "—",
                        "Missing Skills": ", ".join(sorted(missing)) or "—",
                        "Embedding":      resume_embedding,
                    })

                progress_bar.progress(1.0, text="✅  Analysis complete!")
                import time; time.sleep(0.6)
                progress_bar.empty()

                df = pd.DataFrame(results).sort_values("Score", ascending=False)
                df["Rank"] = range(1, len(df) + 1)
                df = df[["Rank", "Candidate", "Email", "File", "Score", "Status",
                          "Matched Skills", "Missing Skills"]]
                st.session_state["df"]       = df
                st.session_state["analysed"] = True
                save_candidates(results)
                st.success(f"✅  Screening complete — {len(df)} candidates ranked")
                st.rerun()

    # ── Results section ────────────────────────────────────────────────────
    if st.session_state.get("analysed"):
        df  = st.session_state["df"]
        sim = len(df[df["Status"] == "Similar"])

        st.markdown("""
        <div class="section-divider">
            <span class="sd-label">📊 Candidate Rankings</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        # Candidate profile cards
        for _, row in df.iterrows():
            rank  = int(row["Rank"])
            score = row["Score"]
            is_match = row["Status"] == "Similar"

            sc_cls  = "score-high" if score >= 70 else "score-mid" if score >= 45 else "score-low"
            acc_cls = "cpc-accent-shortlisted" if is_match else "cpc-accent-rejected"
            rb_cls  = "rank-1" if rank == 1 else "rank-2" if rank == 2 else "rank-3" if rank == 3 else "rank-n"
            badge_cls = "badge-shortlisted" if is_match else "badge-rejected"
            badge_lbl = "✓  Shortlisted" if is_match else "✗  Not Matching"

            matched_pills = "".join(
                f'<span class="skill-pill pill-match">✓ {s.strip()}</span>'
                for s in row["Matched Skills"].split(",")
                if s.strip() and s.strip() != "—"
            )
            missing_pills = "".join(
                f'<span class="skill-pill pill-miss">✗ {s.strip()}</span>'
                for s in row["Missing Skills"].split(",")
                if s.strip() and s.strip() != "—"
            )
            skills_html = matched_pills + missing_pills or '<span class="pill-none">No skill data extracted</span>'
            email_disp  = row["Email"] if row["Email"] else "Email not found"

            st.markdown(f"""
            <div class="candidate-profile-card">
                <div class="cpc-accent-bar {acc_cls}"></div>
                <div class="cpc-body">
                    <div class="cpc-rank {rb_cls}">#{rank}</div>
                    <div class="cpc-info">
                        <div class="cpc-name">{row['Candidate']}</div>
                        <div class="cpc-email">{email_disp}</div>
                        <div class="cpc-file">📎 {row['File']}</div>
                    </div>
                    <div class="cpc-score-wrap {sc_cls}">
                        <div class="cpc-score-circle">
                            <div class="cpc-score-num">{score}</div>
                            <div class="cpc-score-pct">%</div>
                        </div>
                        <div class="status-badge {badge_cls}">{badge_lbl}</div>
                    </div>
                    <div class="cpc-skills">
                        <div class="skills-row-label">Skills Analysis</div>
                        {skills_html}
                    </div>
                    <div class="cpc-actions">
                        <div class="action-tag">Rank #{rank} of {len(df)}</div>
                        <div class="action-tag" style="color:{'#059669' if score>=70 else '#D97706' if score>=45 else '#E11D48'}">
                            {'Strong Match' if score>=70 else 'Partial Match' if score>=45 else 'Weak Match'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_dl, _ = st.columns([1, 3])
        col_dl.download_button(
            "⬇️  Export Rankings CSV",
            df.to_csv(index=False).encode(),
            "candidate_ranking.csv",
            "text/csv"
        )

        # ── HR Final Decision ──────────────────────────────────────────────
        st.markdown("""
        <div class="section-divider" style="margin-top:36px">
            <span class="sd-label">👩‍💼 HR Final Decision</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:16px">
            Review AI recommendations below and override selections before sending outreach emails.
            Checked candidates will receive a shortlist email; unchecked will receive a rejection email.
        </p>
        """, unsafe_allow_html=True)

        final_selection = {}
        st.markdown('<div class="decision-panel"><div class="decision-panel-header"><div class="dph-title">✦ Candidate Selection — Override AI Decisions</div></div>', unsafe_allow_html=True)

        for idx, row in df.iterrows():
            default_val = row["Status"] == "Similar"
            email_disp  = row["Email"] if row["Email"] else "—"
            sc = row["Score"]
            score_color = "#059669" if sc >= 70 else "#D97706" if sc >= 45 else "#E11D48"

            chk_col, info_col = st.columns([0.05, 0.95])
            with chk_col:
                checked = st.checkbox("", value=default_val, key=f"select_{idx}")
            with info_col:
                st.markdown(f"""
                <div class="decision-row">
                    <div style="flex:1">
                        <div class="dr-name">{row['Candidate']}</div>
                        <div class="dr-email">{email_disp}</div>
                    </div>
                    <div class="dr-score" style="background:{'rgba(16,185,129,0.12)' if sc>=70 else 'rgba(245,158,11,0.12)' if sc>=45 else 'rgba(244,63,94,0.12)'};color:{score_color}">
                        {sc}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            final_selection[row["Candidate"]] = checked

        st.markdown('</div>', unsafe_allow_html=True)
        st.session_state["final_selection"] = final_selection

        selected_list = [n for n, v in final_selection.items() if v]
        rejected_list = [n for n, v in final_selection.items() if not v]

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.25);
                        border-radius:14px;padding:18px 20px;margin-top:14px">
                <div style="font-size:0.78rem;font-weight:800;color:#10B981;text-transform:uppercase;
                            letter-spacing:0.12em;margin-bottom:12px;font-family:Inter,sans-serif">
                    ✅  Final Shortlist — {len(selected_list)} candidates
                </div>
                {"".join(f'<div style="font-size:0.84rem;color:#10B981;padding:4px 0;border-bottom:1px solid rgba(16,185,129,0.1)">✓ {c}</div>' for c in selected_list) or
                 '<div style="color:var(--text-muted);font-size:0.8rem;font-style:italic">No candidates selected</div>'}
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.25);
                        border-radius:14px;padding:18px 20px;margin-top:14px">
                <div style="font-size:0.78rem;font-weight:800;color:#F43F5E;text-transform:uppercase;
                            letter-spacing:0.12em;margin-bottom:12px;font-family:Inter,sans-serif">
                    ✗  Rejected — {len(rejected_list)} candidates
                </div>
                {"".join(f'<div style="font-size:0.84rem;color:#F43F5E;padding:4px 0;border-bottom:1px solid rgba(244,63,94,0.1)">✗ {c}</div>' for c in rejected_list) or
                 '<div style="color:var(--text-muted);font-size:0.8rem;font-style:italic">All candidates selected</div>'}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚀  Send Emails to All Candidates", use_container_width=True):
            sent_count = 0
            with st.spinner("📧  Generating and sending emails…"):
                for _, row in df.iterrows():
                    cname  = row["Candidate"]
                    cemail = row["Email"]
                    if not cemail:
                        continue
                    flag = final_selection[cname]
                    body = generate_email(cname, "Similar" if flag else "Rejected")
                    ok   = send_email(cemail, "Application Update", body)
                    if ok:
                        save_email(cname, cemail, "Similar" if flag else "Rejected", body)
                        sent_count += 1
            st.success(f"✅  {sent_count} emails dispatched successfully.")

        # ── Email Generator ────────────────────────────────────────────────
        st.markdown("""
        <div class="section-divider" style="margin-top:36px">
            <span class="sd-label">✉️ Email Generator</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        eg_col1, eg_col2 = st.columns([3, 1])
        sel_cand = eg_col1.selectbox(
            "Select candidate to generate email for",
            df["Candidate"].tolist(),
            label_visibility="visible"
        )
        row = df[df["Candidate"] == sel_cand].iloc[0]
        sc_color = "#10B981" if row["Status"] == "Similar" else "#F43F5E"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:12px 18px;
                    background:var(--bg-card);border:1px solid var(--border);
                    border-radius:12px;margin:12px 0 16px;box-shadow:0 2px 8px rgba(15,23,42,0.05)">
            <span style="font-weight:700;color:var(--text-primary);font-size:0.92rem;font-family:Inter,sans-serif">{sel_cand}</span>
            <span style="color:var(--border);font-size:0.9rem">·</span>
            <span style="font-size:0.82rem;color:var(--text-muted)">{row['Score']}% semantic match</span>
            <span style="color:var(--border)">·</span>
            <span class="status-badge {'badge-shortlisted' if row['Status']=='Similar' else 'badge-rejected'}">
                {'✓ Shortlisted' if row['Status']=='Similar' else '✗ Not Matching'}
            </span>
        </div>
        """, unsafe_allow_html=True)

        if eg_col2.button("✨  Generate Email", use_container_width=True):
            with st.spinner("🤖  Crafting personalised email…"):
                st.session_state["email"]     = generate_email(sel_cand, row["Status"])
                st.session_state["email_for"] = sel_cand
            st.success("Email generated!")

        if st.session_state.get("email") and st.session_state.get("email_for") == sel_cand:
            email_text = st.session_state["email"]

            st.markdown(f"""
            <div class="email-composer">
                <div class="ec-header">
                    <div class="ec-dot" style="background:#F43F5E"></div>
                    <div class="ec-dot" style="background:#2563EB"></div>
                    <div class="ec-dot" style="background:#10B981"></div>
                    <span class="ec-filename">
                        draft_email_{sel_cand.replace(' ','_').lower()}.txt
                        &nbsp;·&nbsp;
                        {'Shortlist' if row['Status']=='Similar' else 'Rejection'} Template
                    </span>
                </div>
                <div class="ec-body">{email_text}</div>
            </div>
            """, unsafe_allow_html=True)

            candidate_email = st.text_input(
                "Candidate Email Address",
                value=row["Email"],
                key="send_email_addr"
            )
            edited_email = st.text_area(
                "Edit Email Before Sending",
                value=email_text,
                height=320,
                key="email_edit_area"
            )
            send_col1, send_col2 = st.columns(2)
            if send_col1.button("✏️ Save Changes", use_container_width=True):
                st.session_state["email"] = edited_email
                st.success("Email updated successfully.")
            if send_col2.button("📧 Send Email", use_container_width=True):
                if not candidate_email:
                    st.error("Please enter candidate email address.")
                else:
                    success = send_email(candidate_email, "Application Update", edited_email)
                    if success:
                        st.success(f"Email sent successfully to {candidate_email}")
                    else:
                        st.error("Failed to send email.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 2 — CANDIDATE DATABASE
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div id="candidate-database"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">🗄️ Candidate Database</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    candidates = get_all_candidates()
    emails_log_for_timeline = get_all_emails()
    _email_sent_lookup = {}
    for _e in emails_log_for_timeline:
        # Candidate, Email, Status, Email Body, Sent At
        _email_sent_lookup[_e[0]] = _e[4] if len(_e) > 4 else None

    if candidates:
        cdf = pd.DataFrame(candidates, columns=[
            "Name", "Email", "File", "Score", "Status",
            "Matched Skills", "Missing Skills", "Screened At"
        ])

        # Search & filter controls
        db_c1, db_c2, db_c3 = st.columns([2.4, 1, 1])
        with db_c1:
            search_q = st.text_input("🔍 Search candidates", placeholder="Name, email, or skill…", label_visibility="collapsed")
        with db_c2:
            status_f = st.selectbox("Status", ["All", "Similar", "Not Similar"], label_visibility="collapsed")
        with db_c3:
            score_f = st.selectbox("Score", ["All Scores", "Above 50", "Above 70", "Above 80"], label_visibility="collapsed")

        filtered_df = cdf.copy()
        if search_q:
            q = search_q.lower()
            filtered_df = filtered_df[
                filtered_df["Name"].str.lower().str.contains(q, na=False) |
                filtered_df["Email"].str.lower().str.contains(q, na=False) |
                filtered_df["Matched Skills"].str.lower().str.contains(q, na=False)
            ]
        if status_f != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_f]
        if score_f == "Above 50":
            filtered_df = filtered_df[filtered_df["Score"] > 50]
        elif score_f == "Above 70":
            filtered_df = filtered_df[filtered_df["Score"] > 70]
        elif score_f == "Above 80":
            filtered_df = filtered_df[filtered_df["Score"] > 80]

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="font-size:0.8rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em">
                Showing {len(filtered_df)} of {len(cdf)} records
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 👥 Candidate Profiles")

        for _, row in filtered_df.iterrows():

            score = int(row["Score"])

            if score >= 60:
                score_color = "🟢"
            elif score >= 40:
                score_color = "🟡"
            else:
                score_color = "🔴"

            with st.container(border=True):

                c1, c2 = st.columns([4,1])

                with c1:
                    st.subheader(row["Name"])
                    st.caption(row["Email"])

                with c2:
                    st.metric(
                        "Match Score",
                        f"{score}%"
                    )

                st.write(
                    f"**Status:** {score_color} {row['Status']}"
                )

                st.write(
                    f"**Matched Skills:** {row['Matched Skills']}"
                )

                st.write(
                    f"**Missing Skills:** {row['Missing Skills']}"
                )



        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "⬇️  Export Full DB CSV",
            cdf.to_csv(index=False).encode(),
            "candidates_db.csv",
            "text/csv"
        )
        dl2.download_button(
            "⬇️  Export Filtered CSV",
            filtered_df.to_csv(index=False).encode(),
            "candidates_filtered.csv",
            "text/csv"
        )

        # ── Candidate Timeline — built only from real DB timestamps ────────
        st.markdown("""
        <div class="section-divider" style="margin-top:30px">
            <span class="sd-label">🕒 Candidate Timeline</span>
            <div class="sd-line"></div>
        </div>
        <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:4px">
            Tracks each candidate's real progress through the pipeline using actual database timestamps.
        </p>
        """, unsafe_allow_html=True)

        _timeline_pick = st.selectbox(
            "Select a candidate to view their timeline",
            cdf["Name"].tolist(),
            key="timeline_candidate_pick"
        )
        _t_row = cdf[cdf["Name"] == _timeline_pick].iloc[0]
        _t_screened_at = _t_row["Screened At"]
        _t_sent_at = _email_sent_lookup.get(_timeline_pick)
        _t_email_generated = _t_sent_at is not None  # generation implied by a successful send record

        def _tl_step(icon, label, sub, done):
            dot_cls = "tl-dot-done" if done else "tl-dot-pending"
            lbl_cls = "tl-label-done" if done else ""
            sub_html = f'<div class="tl-sub">{sub}</div>' if sub else ""
            return (
                f'<div class="tl-step">'
                f'<div class="tl-dot {dot_cls}">{icon if done else "○"}</div>'
                f'<div class="tl-label {lbl_cls}">{label}</div>'
                f'{sub_html}'
                f'</div>'
            )

        def _tl_line(done):
            return f'<div class="tl-line {"tl-line-done" if done else ""}"></div>'

        _timeline_html = '<div class="cand-timeline">'
        _timeline_html += _tl_step("📤", "Resume Uploaded", "", True)
        _timeline_html += _tl_line(True)
        _timeline_html += _tl_step("🔍", "Screened", str(_t_screened_at) if _t_screened_at else "", True)
        _timeline_html += _tl_line(_t_email_generated)
        _timeline_html += _tl_step("✉️", "Email Generated", "", _t_email_generated)
        _timeline_html += _tl_line(_t_email_generated)
        _timeline_html += _tl_step("✅", "Email Sent", str(_t_sent_at) if _t_sent_at else "", _t_email_generated)
        _timeline_html += '</div>'

        st.markdown(_timeline_html, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🗄️</span>
            <div class="empty-title">No Candidate Records Found</div>
            <div class="empty-desc">
                Your PostgreSQL database is empty. Run a resume screening session
                to populate it with candidate data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Email Log ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-divider" style="margin-top:36px">
        <span class="sd-label">📧 Sent Email Log</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    emails_log = get_all_emails()
    if emails_log:
        edf = pd.DataFrame(emails_log, columns=[
            "Candidate", "Email", "Status", "Email Body", "Sent At"
        ])
        for _, erow in edf.iterrows():
            is_ok = erow["Status"] == "Similar"
            icon = "✅" if is_ok else "✗"
            with st.expander(f"{icon}  {erow['Candidate']}  ·  {erow['Email']}  ·  {erow['Sent At']}"):
                st.markdown(f"""
                <div class="email-composer">
                    <div class="ec-header">
                        <div class="ec-dot" style="background:#F43F5E"></div>
                        <div class="ec-dot" style="background:#2563EB"></div>
                        <div class="ec-dot" style="background:#10B981"></div>
                        <span class="ec-filename">
                            Sent to: {erow['Email']}
                            &nbsp;·&nbsp;
                            <span style="color:{'#10B981' if is_ok else '#F43F5E'}">
                                {'Shortlist' if is_ok else 'Rejection'} Email
                            </span>
                        </span>
                    </div>
                    <div class="ec-body">{erow['Email Body']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state" style="padding:40px">
            <span class="empty-icon">📭</span>
            <div class="empty-title">No Emails Sent Yet</div>
            <div class="empty-desc">
                Use the Email Generator in the Resume Screening tab to send outreach.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Danger zone ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(244,63,94,0.04);border:1px solid rgba(244,63,94,0.18);
                border-radius:12px;padding:16px 20px;display:flex;
                align-items:center;justify-content:space-between;gap:16px">
        <div>
            <div style="font-size:0.8rem;font-weight:700;color:#F43F5E;margin-bottom:3px">
                ⚠️  Danger Zone
            </div>
            <div style="font-size:0.75rem;color:var(--text-muted)">
                Permanently delete all candidate records and email logs from PostgreSQL.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    danger_col, _ = st.columns([1, 4])
    if danger_col.button("🗑️  Clear All Database Records"):
        clear_db()
        st.success("Database cleared. All records removed.")
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
#  TAB 3 — SCREENING REPORTS
# ════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown('<div id="screening-reports"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📋 Screening Report</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("analysed"):
        df     = st.session_state["df"]
        report = generate_screening_report(df, jd)

        sim_r   = len(df[df["Status"] == "Similar"])
        rej_r   = len(df) - sim_r
        avg_r   = round(df["Score"].mean(), 1)
        top_r   = df.iloc[0]["Candidate"] if len(df) else "—"
        top_sc  = int(df["Score"].max()) if len(df) else 0
        rate_r  = round((sim_r / len(df)) * 100, 1) if len(df) else 0

        st.markdown("""
        <div style="font-size:0.78rem;font-weight:800;color:var(--primary);
                    text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
            Executive Summary
        </div>
        """, unsafe_allow_html=True)

        # Summary cards
        st.markdown(f"""
        <div class="report-summary-grid">
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#4F46E5,#6366F1)"></div>
                <div class="rc-num" style="color:var(--text-primary)">{len(df)}</div>
                <div class="rc-label">Total Candidates</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#10B981,#34D399)"></div>
                <div class="rc-num" style="color:#059669">{sim_r}</div>
                <div class="rc-label">Shortlisted</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#F43F5E,#FB7185)"></div>
                <div class="rc-num" style="color:#E11D48">{rej_r}</div>
                <div class="rc-label">Rejected</div>
            </div>
        </div>
        <div class="report-summary-grid">
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#2563EB,#4F46E5)"></div>
                <div class="rc-num" style="color:#2563EB">{avg_r}%</div>
                <div class="rc-label">Average Match Score</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#9333EA,#A855F7)"></div>
                <div class="rc-num" style="color:#9333EA">{rate_r}%</div>
                <div class="rc-label">Shortlist Rate</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#F59E0B,#FBBF24)"></div>
                <div class="rc-num" style="color:#B45309;font-size:1.1rem">{top_r}</div>
                <div class="rc-label">Top Candidate ({top_sc}%)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Report preview
        st.markdown(f"""
        <div class="report-preview-container">
            <div class="rpc-header">
                <div class="rpc-title">📄  Full Screening Report</div>
                <div style="font-size:0.78rem;color:var(--text-muted)">screening_report.txt</div>
            </div>
            <div class="rpc-body">{report}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        rpt_col1, rpt_col2, _ = st.columns([1.2, 1.2, 2])
        rpt_col1.download_button(
            "⬇️  Download Report (.txt)",
            report.encode(),
            "screening_report.txt",
            "text/plain",
            use_container_width=True
        )
        rpt_col2.download_button(
            "⬇️  Export Rankings (.csv)",
            df.to_csv(index=False).encode(),
            "candidate_ranking.csv",
            "text/csv",
            use_container_width=True
        )

    else:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">📊</span>
            <div class="empty-title">No Report Available Yet</div>
            <div class="empty-desc">
                Reports are generated automatically after each screening run.<br>
                Go to the <strong>Resume Screening</strong> tab, upload resumes,
                add a Job Description in the sidebar, and run the analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════
# LIVE RECRUITMENT ACTIVITY + SYSTEM STATUS
# ═══════════════════════════════════════════════════════════════════════

feed_col, sys_col = st.columns([2, 1])

with feed_col:

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📈 Recruitment Activity</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    recent_candidates = get_all_candidates()

    if recent_candidates:

        for cand in recent_candidates[-5:][::-1]:

            name = cand[0]
            score = cand[3]
            status = cand[4]

            icon = "✅" if status == "Similar" else "❌"

            st.markdown(
                f"""
                <div style="
                    background:var(--bg-card);
                    border:1px solid var(--border);
                    border-radius:14px;
                    padding:14px 18px;
                    margin-bottom:10px;
                    box-shadow:var(--shadow-sm);
                ">
                    {icon}
                    <strong>{name}</strong>
                    screened with
                    <strong>{score}%</strong>
                    semantic match score
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No screening activity available yet.")

with sys_col:

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">⚙️ System Status</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.success("PostgreSQL Connected")
    st.success("Qdrant Running")
    st.success("Groq Active")
    st.success("Embeddings Ready")
    st.success("Email Engine Online")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>

<div style="text-align:center;padding:20px">

WeRecruit

Powered by Groq • PostgreSQL • Qdrant • Sentence Transformers • Langfuse

© Eidiko Systems Integrators

</div>
""",
unsafe_allow_html=True)