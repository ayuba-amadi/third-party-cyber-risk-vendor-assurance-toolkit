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
    st.set_page_config(page_title=APPLICATION_NAME, layout="wide")
    navigation = st.navigation([
        st.Page(f"pages/{filename}.py", title=title, default=index == 0)
        for index, (title, filename) in enumerate(PAGES)
    ])
    navigation.run()


if __name__ == "__main__":
    main()
