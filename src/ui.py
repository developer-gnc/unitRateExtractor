import base64
import html as html_lib
from typing import Dict, List
import streamlit as st
import pandas as pd


@st.cache_data(show_spinner=False)
def get_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_header(page_title: str, logo_path: str):
    st.set_page_config(page_title=page_title, layout="wide")
    logo_b64 = get_base64_image(logo_path)

    st.markdown(
        f"""
        <style>
          .block-container {{
              max-width: 100% !important;
              padding-top: 4.5rem;
              padding-left: 2rem;
              padding-right: 2rem;
          }}
          .header-container {{
              width: 100%;
              display: flex;
              align-items: center;
              gap: 14px;
              padding: 4px 0 6px 0;
          }}
          .header-logo {{ width: 90px; height: auto; }}
          .header-title {{ font-size: 40px; font-weight: 700; line-height: 1.05; margin: 0; }}
          .header-subtitle {{ font-size: 14px; color: #9aa0a6; margin-top: 2px; }}
          .thin-hr {{ margin: 6px 0 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.12); }}
        </style>

        <div class="header-container">
            <img src="data:image/jpeg;base64,{logo_b64}" class="header-logo" />
            <div>
                <div class="header-title">{html_lib.escape(page_title)}</div>
                <div class="header-subtitle">Unit rates by province, city, year &amp; month</div>
            </div>
        </div>
        <hr class="thin-hr" />
        """,
        unsafe_allow_html=True,
    )


def render_controls(
    years: List[str], months: List[str], provinces: List[str], cities: List[str]
) -> Dict:
    st.title("Search in Item Description")

    fuzzy_on = st.checkbox("Fuzzy (typo tolerant)", value=False)
    min_score = st.slider("Fuzzy match strength (higher = stricter)", 50, 95, 70, step=1) if fuzzy_on else 70
    
    query = st.text_input(
        "Type search text (e.g., 'drywall', 'demolition', 'invoice 123')"
    ).strip()
    # limit = st.slider("Max results", 50, 2000, 50, step=50)

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        year_filter = st.selectbox("Invoice Year", years)
    with c2:
        month_filter = st.selectbox("Invoice Month", months)
    with c3:
        province = st.selectbox("Province", provinces)
    with c4:
        city = st.selectbox("City", cities)

    return {
    "query": query,
    "year_filter": year_filter,
    "month_filter": month_filter,
    "province": province,
    "city": city,
    "fuzzy_on": fuzzy_on,
    "min_score": min_score,
    }


def render_results(df: pd.DataFrame):
    df = df.copy()
    df.insert(0, "S. No.", range(1, len(df) + 1))

    st.write(f"Found: {len(df)} rows")

    st.download_button(
        "Download results as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="search_results.csv",
        mime="text/csv",
    )

    return df