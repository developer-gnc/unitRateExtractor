import sqlite3
import pandas as pd
import streamlit as st
import base64
import html


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_table(df: pd.DataFrame):
    """
    Renders a styled HTML table:
    - All headers centered
    - All cells centered
    - Item Description wrapped
    - Max widths capped
    - Scrollable container
    """

    # Escape HTML so user text can't break your page
    safe_df = df.copy()
    for col in safe_df.columns:
        safe_df[col] = safe_df[col].astype(str).map(html.escape)

    # Build HTML table
    table_html = safe_df.to_html(index=False, escape=False, classes="custom-table")

    st.markdown(
        """
        <style>
        .table-wrap {
            width: 100%;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 520px;              /* scroll height */
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
        }

        table.custom-table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;            /* enables max-width + wrapping */
            font-size: 13px;
        }

        table.custom-table thead th {
            position: sticky;
            top: 0;
            z-index: 5;
            background: rgba(20, 22, 28, 0.95);
            text-align: center !important;
            font-weight: 700;
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
        }

        table.custom-table tbody td {
            text-align: center !important;
            padding: 8px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            white-space: nowrap;            /* default: no wrap */
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 220px;               /* cap for most columns */
        }

        /* Hover */
        table.custom-table tbody tr:hover td {
            background: rgba(255,255,255,0.04);
        }

        /* --- Column specific widths (adjust if you want) --- */
        /* 1 S. No. */
        table.custom-table th:nth-child(1), table.custom-table td:nth-child(1) { max-width: 70px;  width: 70px; }
        /* 2 Invoice Year */
        table.custom-table th:nth-child(2), table.custom-table td:nth-child(2) { max-width: 110px; width: 110px; }
        /* 3 Invoice Month */
        table.custom-table th:nth-child(3), table.custom-table td:nth-child(3) { max-width: 140px; width: 140px; }
        /* 4 Province */
        table.custom-table th:nth-child(4), table.custom-table td:nth-child(4) { max-width: 160px; width: 160px; }
        /* 5 City */
        table.custom-table th:nth-child(5), table.custom-table td:nth-child(5) { max-width: 160px; width: 160px; }
        /* 7 UOM */
        table.custom-table th:nth-child(7), table.custom-table td:nth-child(7) { max-width: 90px;  width: 90px; }
        /* 8 Unit Rate */
        table.custom-table th:nth-child(8), table.custom-table td:nth-child(8) { max-width: 110px; width: 110px; }

        /* --- Item Description (6th column): wrap + wider cap --- */
        table.custom-table tbody td:nth-child(6) {
            text-align: left !important;    /* change to center if you want */
            white-space: normal !important;
            overflow: visible;
            text-overflow: clip;
            max-width: 560px;
            width: 560px;
            word-break: break-word;
            line-height: 1.25;
        }

        /* Keep Item Description header centered */
        table.custom-table thead th:nth-child(6) {
            text-align: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="table-wrap">{table_html}</div>', unsafe_allow_html=True)


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Unit Rate Explorer", layout="wide")
LOGO_BASE64 = get_base64_image("logo.jpg")  # or logo.png

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
        <img src="data:image/jpeg;base64,{LOGO_BASE64}" class="header-logo" />
        <div>
            <div class="header-title">Unit Rate Explorer</div>
            <div class="header-subtitle">Unit rates by province, city, year &amp; month</div>
        </div>
    </div>
    <hr class="thin-hr" />
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Your existing DB code
# -----------------------------
DB_PATH = "data.db"
TABLE = "records"

st.title("Search in Item Description")

query = st.text_input("Type search text (e.g., 'drywall', 'demolition', 'invoice 123')").strip()
limit = st.slider("Max results", 50, 2000, 200, step=50)

conn = sqlite3.connect(DB_PATH)

year_df = pd.read_sql_query(
    f'''SELECT DISTINCT "Invoice Year" AS year FROM "{TABLE}" WHERE "Invoice Year" IS NOT NULL ORDER BY year''',
    conn
)
month_df = pd.read_sql_query(
    f'''SELECT DISTINCT "Invoice Month" AS month_num, "Invoice Month Name" AS month_name
        FROM "{TABLE}" WHERE "Invoice Month" IS NOT NULL ORDER BY month_num''',
    conn
)
prov_df = pd.read_sql_query(
    f'''SELECT DISTINCT "Province" AS province FROM "{TABLE}" WHERE "Province" IS NOT NULL ORDER BY province''',
    conn
)
city_df = pd.read_sql_query(
    f'''SELECT DISTINCT "City" AS city FROM "{TABLE}" WHERE "City" IS NOT NULL ORDER BY city''',
    conn
)

years = ["(All)"] + year_df["year"].dropna().astype(int).astype(str).tolist()
months = ["(All)"] + month_df["month_name"].dropna().tolist()
provinces = ["(All)"] + prov_df["province"].dropna().tolist()
cities = ["(All)"] + city_df["city"].dropna().tolist()

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

month_name_to_num = dict(zip(month_df["month_name"], month_df["month_num"]))

if query:
    where = ['"Item Description" LIKE ?']
    params = [f"%{query}%"]

    if year_filter != "(All)":
        where.append('"Invoice Year" = ?')
        params.append(int(year_filter))
    if month_filter != "(All)":
        where.append('"Invoice Month" = ?')
        params.append(int(month_name_to_num[month_filter]))
    if province != "(All)":
        where.append('"Province" = ?')
        params.append(province)
    if city != "(All)":
        where.append('"City" = ?')
        params.append(city)

    where_sql = " AND ".join(where)

    sql = f'''
        SELECT
            "Invoice Year"          AS "Invoice Year",
            "Invoice Month Name"    AS "Invoice Month",
            "Province"              AS "Province",
            "City"                  AS "City",
            "Item Description"      AS "Item Description",
            "UOM"                   AS "UOM",
            "Unit Rate"             AS "Unit Rate"
        FROM "{TABLE}"
        WHERE {where_sql}
        LIMIT ?
    '''
    params.append(limit)

    df = pd.read_sql_query(sql, conn, params=params)
    df.insert(0, "S. No.", range(1, len(df) + 1))

    st.write(f"Found: {len(df)} rows")

    # ✅ Reliable centered + wrapped table
    render_table(df)

    st.download_button(
        "Download results as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="search_results.csv",
        mime="text/csv"
    )
else:
    st.info("Enter text to search.")

conn.close()
