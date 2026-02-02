import pandas as pd

def format_output_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Invoice Year: 2025.0 -> 2025
    if "Invoice Year" in df.columns:
        df["Invoice Year"] = pd.to_numeric(df["Invoice Year"], errors="coerce").astype("Int64")
        df["Invoice Year"] = df["Invoice Year"].astype(str).replace("<NA>", "")

    # Unit Rate: optional (keeps clean display)
    # if "Unit Rate" in df.columns:
    #     df["Unit Rate"] = pd.to_numeric(df["Unit Rate"], errors="coerce")

    return df