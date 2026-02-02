from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    page_title: str = "Unit Rate Explorer"
    layout: str = "wide"
    db_path: str = "data.db"
    table: str = "records"
    logo_path: str = "logo.jpg"  # or logo.png
    max_table_height_px: int = 520

CONFIG = AppConfig()
