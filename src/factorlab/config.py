from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "factorlab.duckdb"
UNIVERSE_PATH = DATA_DIR / "universe.csv"

#iShares do not use hyphen
TICKER_FIXES = {"BRKB": "BRK-B", "BFB": "BF-B"}

START_DATE = "2015-01-01"
BATCH_SIZE = 50
MAX_RETRIES = 3
PAUSE_SECONDS = 2
