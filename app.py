import streamlit as st
from src.config import CONFIG
from src.db import (
    load_filter_options,
    build_search_sql,
    run_search,
    build_candidate_sql,
    fuzzy_rank_results,
)
from src.ui import render_header, render_controls, render_results
from src.render import render_table
from src.format import format_output_df

def main():
    render_header(CONFIG.page_title, CONFIG.logo_path)

    years, months, provinces, cities, month_name_to_num = load_filter_options(
        CONFIG.db_path, CONFIG.table
    )

    controls = render_controls(years, months, provinces, cities)

    if not controls["query"]:
        st.info("Enter text to search.")
        return

    if controls.get("fuzzy_on"):
        # 1) Pull candidates using filters only
        cand_sql, cand_params = build_candidate_sql(
            table=CONFIG.table,
            year_filter=controls["year_filter"],
            month_filter=controls["month_filter"],
            province=controls["province"],
            city=controls["city"],
            month_name_to_num=month_name_to_num,
            candidate_limit=10000,  # ok for your total size
        )
        candidates = run_search(CONFIG.db_path, cand_sql, cand_params)

        # 2) Fuzzy rank in Python
        df = fuzzy_rank_results(
            candidates,
            query=controls["query"],
            limit=controls["limit"],
            min_score=controls["min_score"],
        )
        df = df.drop(columns=["_score", "Score", "_rowid"], errors="ignore")
        st.caption("Fuzzy search is ON (typo tolerant). Results ranked by Score.")

    else:
        # Standard LIKE search
        sql, params = build_search_sql(
            table=CONFIG.table,
            query=controls["query"],
            year_filter=controls["year_filter"],
            month_filter=controls["month_filter"],
            province=controls["province"],
            city=controls["city"],
            month_name_to_num=month_name_to_num,
            limit=controls["limit"],
        )
        df = run_search(CONFIG.db_path, sql, params)
        df = df.drop(columns=["_score", "Score", "_rowid"], errors="ignore")

    df = format_output_df(df)
    df = render_results(df)
    render_table(df, max_height_px=CONFIG.max_table_height_px)


if __name__ == "__main__":
    main()