import sqlite3
import pandas as pd
from typing import Dict, List, Tuple
import streamlit as st
from rapidfuzz import process, fuzz

def get_conn(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path, check_same_thread=False)


@st.cache_data(show_spinner=False)
def load_filter_options(
    db_path: str, table: str
) -> Tuple[List[str], List[str], List[str], List[str], Dict[str, int]]:
    """
    Returns: years, months(names), provinces, cities, month_name_to_num
    """
    conn = get_conn(db_path)

    year_df = pd.read_sql_query(
        f'''SELECT DISTINCT "Invoice Year" AS year FROM "{table}" WHERE "Invoice Year" IS NOT NULL ORDER BY year''',
        conn,
    )
    month_df = pd.read_sql_query(
        f'''SELECT DISTINCT "Invoice Month" AS month_num, "Invoice Month Name" AS month_name
            FROM "{table}" WHERE "Invoice Month" IS NOT NULL ORDER BY month_num''',
        conn,
    )
    prov_df = pd.read_sql_query(
        f'''SELECT DISTINCT "Province" AS province FROM "{table}" WHERE "Province" IS NOT NULL ORDER BY province''',
        conn,
    )
    city_df = pd.read_sql_query(
        f'''SELECT DISTINCT "City" AS city FROM "{table}" WHERE "City" IS NOT NULL ORDER BY city''',
        conn,
    )

    conn.close()

    years = ["(All)"] + year_df["year"].dropna().astype(int).astype(str).tolist()
    months = ["(All)"] + month_df["month_name"].dropna().tolist()
    provinces = ["(All)"] + prov_df["province"].dropna().tolist()
    cities = ["(All)"] + city_df["city"].dropna().tolist()
    month_name_to_num = dict(zip(month_df["month_name"], month_df["month_num"]))

    return years, months, provinces, cities, month_name_to_num

def tokenize(q: str):
    import re
    q = q.lower()
    terms = re.findall(r"[a-z0-9]+", q)
    stop = {"and","or","the","a","an","to","of","for","in","on","with"}
    terms = [t for t in terms if t not in stop and len(t) >= 2]
    return terms

def build_search_sql(
    table: str,
    query: str,
    year_filter: str,
    month_filter: str,
    province: str,
    city: str,
    month_name_to_num: Dict[str, int],
):

    # --- NEW: tokenize and AND each token ---
    terms = tokenize(query)

    # WHERE: require all tokens (AND)
    where = []
    where_params = []

    if terms:
        for t in terms:
            where.append('LOWER("Item Description") LIKE ?')
            where_params.append(f"%{t}%")
    else:
        where.append('LOWER("Item Description") LIKE ?')
        where_params.append(f"%{query.lower().strip()}%")

    # Score: count how many tokens match (for sorting)
    if terms:
        score_exprs = ['CASE WHEN LOWER("Item Description") LIKE ? THEN 1 ELSE 0 END' for _ in terms]
        score_sql = "(" + " + ".join(score_exprs) + ")"   # <-- parentheses are correct now
        score_params = [f"%{t}%" for t in terms]
    else:
        score_sql = "0"
        score_params = []

    # Filters
    if year_filter != "(All)":
        where.append('"Invoice Year" = ?')
        where_params.append(int(year_filter))
    if month_filter != "(All)":
        where.append('"Invoice Month" = ?')
        where_params.append(int(month_name_to_num[month_filter]))
    if province != "(All)":
        where.append('"Province" = ?')
        where_params.append(province)
    if city != "(All)":
        where.append('"City" = ?')
        where_params.append(city)

    where_sql = " AND ".join(where)

    sql = f'''
        SELECT
            {score_sql} AS _score,
            "Invoice Year"          AS "Invoice Year",
            "Invoice Month Name"    AS "Invoice Month",
            "Province"              AS "Province",
            "City"                  AS "City",
            "Item Description"      AS "Item Description",
            "UOM"                   AS "UOM",
            "Unit Rate"             AS "Unit Rate",
            "GNC File"             AS "GNC File",
            "File Name"            AS "File Name"
        FROM "{table}"
        WHERE {where_sql}
        ORDER BY _score DESC
    '''
    # IMPORTANT: score params come first, then WHERE params, then LIMIT
    params = score_params + where_params

    return sql, params

#---------Fuzzy Logic----------------------------------

def build_candidate_sql(
    table: str,
    year_filter: str,
    month_filter: str,
    province: str,
    city: str,
    month_name_to_num: Dict[str, int],
    candidate_limit: int = 10000,  # for 10k total rows, ok
):
    """
    Pull candidates based on filters only (no LIKE). Then fuzzy rank in Python.
    """
    where = ['"Item Description" IS NOT NULL']
    params: List = []

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
            rowid as _rowid,
            "Invoice Year"          AS "Invoice Year",
            "Invoice Month Name"    AS "Invoice Month",
            "Province"              AS "Province",
            "City"                  AS "City",
            "Item Description"      AS "Item Description",
            "UOM"                   AS "UOM",
            "Unit Rate"             AS "Unit Rate",
            "GNC File"             AS "GNC File",
            "File Name"            AS "File Name"
        FROM "{table}"
        WHERE {where_sql}
        LIMIT ?
    '''
    params.append(candidate_limit)
    return sql, params


def fuzzy_rank_results(df: pd.DataFrame, query: str, limit: int = 200, min_score: int = 70) -> pd.DataFrame:
    """
    Fuzzy-rank Item Description and return top matches.
    Adds a 'Score' column.
    """
    if df.empty:
        return df

    choices = df["Item Description"].fillna("").astype(str).tolist()

    terms = tokenize(query)
    norm_query = " ".join(terms) if terms else query.strip()

    if not norm_query:
        return df.iloc[0:0].copy()

    # Returns list of tuples: (matched_text, score, index)
    matches = process.extract(
        norm_query,
        choices,
        scorer=fuzz.token_set_ratio, #fuzz.WRatio,
        limit=min(limit * 10, len(choices)),  # grab more then filter by score
    )

    picked = []
    for _, score, idx in matches:
        if score >= min_score:
            picked.append((idx, score))
        if len(picked) >= limit:
            break

    if not picked:
        return df.iloc[0:0].copy()  # empty same columns

    out = df.iloc[[i for i, _ in picked]].copy()
    out.insert(0, "Score", [s for _, s in picked])
    out = out.sort_values("Score", ascending=False)
    return out


def run_search(db_path: str, sql: str, params: List) -> pd.DataFrame:
    conn = get_conn(db_path)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df