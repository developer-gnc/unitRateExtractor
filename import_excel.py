import pandas as pd
import sqlite3

EXCEL_PATH = "master.xlsx"
DB_PATH = "data.db"
TABLE_NAME = "records"

# --- Read both sheets ---
compiled = pd.read_excel(EXCEL_PATH, sheet_name="Compiled Data", header=1)
details  = pd.read_excel(EXCEL_PATH, sheet_name="File Details", header=0)

# --- Clean column names (strip spaces, keep exact names) ---
compiled.columns = [str(c).strip() for c in compiled.columns]
details.columns  = [str(c).strip() for c in details.columns]

# --- Validate required columns ---
required_compiled = {"GNC File", "Item Description"}
required_details  = {"GNC File", "Province", "City"}

missing_c = required_compiled - set(compiled.columns)
missing_d = required_details - set(details.columns)

if missing_c:
    raise ValueError(f"Compiled Data missing columns: {missing_c}")
if missing_d:
    raise ValueError(f"File Details missing columns: {missing_d}")

# --- Reduce details to needed columns + dedupe on GNC File (important) ---
details_small = (
    details[["GNC File", "Province", "City"]]
    .copy()
    .drop_duplicates(subset=["GNC File"], keep="first")
)


# --- Merge Province/City into compiled using GNC File ---
merged = compiled.merge(details_small, on="GNC File", how="left")

# Normalize column names hard (removes leading/trailing + multiple spaces)
merged.columns = [" ".join(str(c).split()) for c in merged.columns]

# --- Clean Invoice Date (date only) ---
if "Invoice Date" in merged.columns:
    merged["Invoice Date"] = pd.to_datetime(
        merged["Invoice Date"], errors="coerce"
    )

    # Extract Year and Month
    merged["Invoice Year"] = merged["Invoice Date"].dt.year
    merged["Invoice Month"] = merged["Invoice Date"].dt.month
    merged["Invoice Month Name"] = merged["Invoice Date"].dt.strftime("%B")

    # Store Invoice Date as ISO date string (no time)
    merged["Invoice Date"] = merged["Invoice Date"].dt.date.astype("string")

# Optional: move Province/City near the front
front_cols = [c for c in ["GNC File", "Province", "City"] if c in merged.columns]
other_cols = [c for c in merged.columns if c not in front_cols]
merged = merged[front_cols + other_cols]

# --- Write to SQLite ---
conn = sqlite3.connect(DB_PATH)
merged.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

# --- Index for faster searches (index the correct column) ---
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_item_desc ON {TABLE_NAME}("Item Description");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_gnc_file ON {TABLE_NAME}("GNC File");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_province ON {TABLE_NAME}("Province");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_city ON {TABLE_NAME}("City");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_invoice_year ON {TABLE_NAME}("Invoice Year");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_invoice_month ON {TABLE_NAME}("Invoice Month");')
conn.execute(f'CREATE INDEX IF NOT EXISTS idx_invoice_month_name ON {TABLE_NAME}("Invoice Month Name");')


conn.commit()
conn.close()

print("Loaded merged data (Compiled Data + Province/City) into data.db successfully.")
