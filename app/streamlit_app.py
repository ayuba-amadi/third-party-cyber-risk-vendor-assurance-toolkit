"""Run from the repository root with streamlit run app/streamlit_app.py."""
from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui_helpers import PAGES
from src.config import APPLICATION_NAME


def main():
    st.set_page_config(page_title="Third-Party Cyber Risk Vendor Assurance Toolkit", page_icon=None,
                       layout="wide", initial_sidebar_state="expanded")
    st.markdown("""<style>
    :root { color-scheme: light; }
    .stApp { background:#F3F4F6; color:#1F2937; }
    [data-testid="stHeader"] { height:2.6rem; background:transparent; }
    [data-testid="stMainBlockContainer"] {
      max-width:1480px; padding-top:1rem; padding-bottom:2rem;
    }
    [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid #E5E7EB; }
    h1 { color:#123B5D; margin:.15rem 0 .25rem; }
    h2, h3 { color:#17324D; }
    [data-testid="stMetric"] {
      background:#FFFFFF; border:1px solid #D1D5DB; border-radius:10px;
      padding:.75rem .9rem; box-shadow:0 1px 2px rgb(15 23 42 / 4%);
    }
    [data-testid="stMetricLabel"] { color:#374151; font-weight:600; }
    [data-testid="stDataFrame"] { border:1px solid #D1D5DB; border-radius:8px; background:#FFFFFF; }
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
    navigation = st.navigation([
        st.Page(f"pages/{filename}.py", title=title, default=index == 0)
        for index, (title, filename) in enumerate(PAGES)
    ])
    navigation.run()


if __name__ == "__main__":
    main()
