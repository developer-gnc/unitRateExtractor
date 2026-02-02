import html
import pandas as pd
import streamlit as st


def _escape_df_for_html(df: pd.DataFrame) -> pd.DataFrame:
    safe_df = df.copy()
    for col in safe_df.columns:
        safe_df[col] = safe_df[col].astype(str).map(html.escape)
    return safe_df


def _inject_table_css(max_height_px: int):
    st.markdown(
        f"""
        <style>
        .table-wrap {{
            width: 100%;
            overflow-x: auto;
            overflow-y: auto;
            max-height: {max_height_px}px;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
            text-align: center;
        }}

        table.custom-table {{
            display: inline-table; 
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            font-size: 13px;
            margin: 0 auto;
        }}

        table.custom-table thead th {{
            position: sticky;
            top: 0;
            z-index: 5;
            background: rgba(20, 22, 28, 0.95);
            text-align: center !important;
            font-weight: 700;
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
        }}

        table.custom-table tbody td {{
            text-align: center !important;
            padding: 8px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 220px;
        }}

        table.custom-table tbody tr:hover td {{
            background: rgba(255,255,255,0.04);
        }}

        /* Column widths */
        table.custom-table th:nth-child(1), table.custom-table td:nth-child(1) {{ max-width: 70px;  width: 70px; }}
        table.custom-table th:nth-child(2), table.custom-table td:nth-child(2) {{ max-width: 110px; width: 110px; }}
        table.custom-table th:nth-child(3), table.custom-table td:nth-child(3) {{ max-width: 140px; width: 140px; }}
        table.custom-table th:nth-child(4), table.custom-table td:nth-child(4) {{ max-width: 160px; width: 160px; }}
        table.custom-table th:nth-child(5), table.custom-table td:nth-child(5) {{ max-width: 160px; width: 160px; }}
        table.custom-table th:nth-child(7), table.custom-table td:nth-child(7) {{ max-width: 90px;  width: 90px; }}
        table.custom-table th:nth-child(8), table.custom-table td:nth-child(8) {{ max-width: 110px; width: 110px; }}

        /* Item Description wrapping (6th column) */
        table.custom-table tbody td:nth-child(6) {{
            text-align: left !important;
            white-space: normal !important;
            overflow: visible;
            text-overflow: clip;
            max-width: 560px;
            min-width: 180px;
            word-break: break-word;
            line-height: 1.25;
        }}

        table.custom-table thead th:nth-child(6) {{
            text-align: center !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_table(df: pd.DataFrame, max_height_px: int = 520):
    _inject_table_css(max_height_px)
    safe_df = _escape_df_for_html(df)
    table_html = safe_df.to_html(index=False, escape=False, classes="custom-table")
    st.markdown(f'<div class="table-wrap">{table_html}</div>', unsafe_allow_html=True)