"""Run from the repository root with streamlit run app/streamlit_app.py."""
from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui_helpers import PAGES, PROJECT_TITLE


def main():
    st.set_page_config(page_title=PROJECT_TITLE, page_icon=None,
                       layout="wide", initial_sidebar_state="auto")
    st.markdown("""<style>
    :root { color-scheme: light; }
    .stApp { background:#F3F4F6; color:#1F2937; }
    [data-testid="stHeader"] { height:2.6rem; background:transparent; }
    [data-testid="stMainBlockContainer"] {
      max-width:1480px; padding-top:1rem; padding-bottom:2rem;
    }
    [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid #E5E7EB; }
    [data-testid="stSidebarHeader"] { height:2.75rem; margin-bottom:0; }
    [data-testid="stSidebarNavItems"] > :first-child > [data-testid="stNavSectionHeader"] p {
      color:#123B5D; font-size:1.05rem; font-weight:700;
    }
    h1 { color:#123B5D; margin:.15rem 0 .25rem; }
    h2, h3 { color:#17324D; }
    [data-testid="stMetric"] {
      background:#FFFFFF; border:1px solid #D1D5DB; border-radius:10px;
      padding:.75rem .9rem; box-shadow:0 1px 2px rgb(15 23 42 / 4%);
    }
    [data-testid="stMetricLabel"] { color:#374151; font-weight:600; }
    .project-title {
      width:100%; font-size:clamp(1.6rem, 3.4vw, 2.7rem); line-height:1.15; padding:0;
      text-align:justify; text-justify:inter-word;
    }
    .project-subtitle {
      color:#374151; padding:.4rem 0 .8rem; margin:0; border-bottom:1px solid #CBD5E1;
    }
    .workflow-steps {
      display:grid; grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));
      gap:.4rem; padding:0; margin:0; list-style-position:inside;
    }
    .workflow-steps li {
      background:#FFF; border:1px solid #CBD5E1; border-radius:6px; padding:.45rem .55rem;
      font-size:.9rem;
    }
    [data-testid="stExpander"] { border-color:#D1D5DB; border-radius:8px; background:#FFFFFF; }
    .status-badge {
      display:inline-flex; align-items:center; min-height:1.5rem; margin:.12rem .15rem .35rem 0;
      padding:.15rem .58rem; border:1px solid var(--badge-border); border-radius:999px;
      background:var(--badge-bg); color:var(--badge-text); font-weight:700; font-size:.82rem;
      line-height:1.25; letter-spacing:.01em;
    }
    .stButton button, .stDownloadButton button { min-height:2.5rem; border-radius:7px; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
      color:#4B5563 !important; opacity:1 !important;
    }
    @media (max-width: 800px) {
      [data-testid="stMainBlockContainer"] { padding: .75rem .85rem 1.5rem; }
      h1 { font-size:1.7rem; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior:auto !important; animation-duration:.01ms !important; }
    }
    </style>""", unsafe_allow_html=True)
    pages = [
        st.Page(f"pages/{filename}.py", title=title, default=index == 0)
        for index, (title, filename) in enumerate(PAGES)
    ]
    navigation = st.navigation({
        "Overview": pages[:2],
        "Assessment": pages[2:4],
        "Decisions and Actions": pages[4:7],
        "Reports and Quality": pages[7:],
    })
    navigation.run()


if __name__ == "__main__":
    main()
