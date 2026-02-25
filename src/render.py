import html
import pandas as pd
import streamlit as st


def _escape_df_for_html(df: pd.DataFrame) -> pd.DataFrame:
    safe_df = df.copy()
    for col in safe_df.columns:
        safe_df[col] = safe_df[col].astype(str).map(html.escape)
    return safe_df


def inject_controls_css():
    st.markdown(
        """
        <style>
        /* =========================
           INPUT BOX (closed state)
           ========================= */

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background-color: #1f2937 !important;
            border: 1px solid rgba(255,255,255,0.8) !important; /* WHITE BORDER */
            border-radius: 8px !important;
        }

        div[data-baseweb="select"] *,
        div[data-baseweb="input"] * {
            color: #ffffff !important;
        }

        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within {
            border: 1px solid #ffffff !important;
            box-shadow: 0 0 0 2px rgba(248,113,113,0.35) !important;
        }

        /* =========================
           DROPDOWN PANEL (OPEN)
           ========================= */

        /* Kill Streamlit default blue everywhere */
        * {
            --primary-color: #f87171 !important;
            --secondary-background-color: #111827 !important;
        }

        div[role="dialog"] div[data-baseweb="menu"],
        div[role="dialog"] [role="listbox"],
        div[data-baseweb="popover"] div[data-baseweb="menu"],
        div[data-baseweb="popover"] [role="listbox"] {
            background-color: #111827 !important;
            border: 1px solid rgba(255,255,255,0.8) !important; /* WHITE BORDER */
            border-radius: 10px !important;
            box-shadow: 0 14px 34px rgba(0,0,0,0.55) !important;
        }

        /* =========================
           OPTIONS
           ========================= */

        div[role="option"],
        li[role="option"],
        div[data-baseweb="option"] {
            background-color: #111827 !important;
            color: #e5e7eb !important;
        }

        /* Hover = LIGHT RED */
        div[role="option"]:hover,
        li[role="option"]:hover,
        div[data-baseweb="option"]:hover {
            background-color: rgba(248,113,113,0.22) !important;
        }

        /* Selected = LIGHT RED */
        div[role="option"][aria-selected="true"],
        li[role="option"][aria-selected="true"],
        div[data-baseweb="option"][aria-selected="true"] {
            background-color: rgba(248,113,113,0.32) !important;
            color: #ffffff !important;
        }

        /* Remove any blue focus ring */
        *:focus {
            outline: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
        /* 1 S. No. */
        table.custom-table th:nth-child(1), table.custom-table td:nth-child(1) {{ max-width: 70px;  width: 70px; }}
        /* 2 Invoice Year */
        table.custom-table th:nth-child(2), table.custom-table td:nth-child(2) {{ max-width: 70px; width: 70px; }}
        /* 3 Invoice Month */
        table.custom-table th:nth-child(3), table.custom-table td:nth-child(3) {{ max-width: 130px; width: 130px; }}
        /* 4 Provnice */
        table.custom-table th:nth-child(4), table.custom-table td:nth-child(4) {{ max-width: 110px; width: 110px; }}
        /* 5 City */
        table.custom-table th:nth-child(5), table.custom-table td:nth-child(5) {{ max-width: 140px; width: 140px; }}
        /* 7 Qty */
        table.custom-table th:nth-child(7), table.custom-table td:nth-child(7) {{ max-width: 70px; width: 70px; }}
        /* 8 UoM */
        table.custom-table th:nth-child(8), table.custom-table td:nth-child(8) {{ max-width: 140px; width: 140px; }}
        /* 9 Unit Rate */
        table.custom-table th:nth-child(9), table.custom-table td:nth-child(9) {{ max-width: 70px; width: 70px; }}
        /* 10 Subtotal */
        table.custom-table th:nth-child(10), table.custom-table td:nth-child(10) {{ max-width: 140px; width: 140px; }}
        /* 11 GNC File  */
        table.custom-table th:nth-child(11), table.custom-table td:nth-child(11) {{ max-width: 70px;  width: 70px; }}
        /* 12 File Name */
        table.custom-table th:nth-child(12), table.custom-table td:nth-child(12) {{ max-width: 110px; width: 110px; word-break: break-word; text-overflow: clip; white-space: normal !important; }}

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