import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd


DATE_CANDIDATES = ["Date", "date", "LocalCodeDate"]

# J-Quants V2 returns O/H/L/C/Vo and adjusted AdjO/AdjH/AdjL/AdjC/AdjVo.
# Prefer adjusted prices because they are usually better for long-term chart analysis.
OPEN_CANDIDATES = ["AdjO", "AdjustmentOpen", "Open", "O", "open", "AdjOpen"]
HIGH_CANDIDATES = ["AdjH", "AdjustmentHigh", "High", "H", "high", "AdjHigh"]
LOW_CANDIDATES = ["AdjL", "AdjustmentLow", "Low", "L", "low", "AdjLow"]
CLOSE_CANDIDATES = ["AdjC", "AdjustmentClose", "Close", "C", "close", "AdjClose"]
VOLUME_CANDIDATES = ["AdjVo", "AdjustmentVolume", "Volume", "Vo", "volume", "AdjVolume"]


def first_existing(df: pd.DataFrame, names: list[str]) -> str:
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(f"None of columns found: {names}. Actual columns: {list(df.columns)}")


def normalize_date(v) -> str:
    dt = pd.to_datetime(v)
    return dt.strftime("%Y.%m.%d")


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"normalize_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    setup_logging(Path(cfg["output"]["log_dir"]))

    code = str(cfg["stock"]["code"])
    raw_csv = Path(cfg["output"]["raw_dir"]) / f"{code}_daily_quotes_raw.csv"
    if not raw_csv.exists():
        # Fallback for display symbol, e.g. raw file may be 4661 while config uses 46610 or vice versa.
        candidates = list(Path(cfg["output"]["raw_dir"]).glob("*_daily_quotes_raw.csv"))
        if len(candidates) == 1:
            raw_csv = candidates[0]
        else:
            raise FileNotFoundError(f"Raw CSV not found: {raw_csv}")

    df = pd.read_csv(raw_csv)
    if df.empty:
        raise RuntimeError(f"Raw CSV is empty: {raw_csv}")

    date_col = first_existing(df, DATE_CANDIDATES)
    open_col = first_existing(df, OPEN_CANDIDATES)
    high_col = first_existing(df, HIGH_CANDIDATES)
    low_col = first_existing(df, LOW_CANDIDATES)
    close_col = first_existing(df, CLOSE_CANDIDATES)

    try:
        volume_col = first_existing(df, VOLUME_CANDIDATES)
    except KeyError:
        volume_col = None

    out_df = pd.DataFrame({
        "Date": df[date_col].apply(normalize_date),
        "Time": "00:00",
        "Open": pd.to_numeric(df[open_col], errors="coerce"),
        "High": pd.to_numeric(df[high_col], errors="coerce"),
        "Low": pd.to_numeric(df[low_col], errors="coerce"),
        "Close": pd.to_numeric(df[close_col], errors="coerce"),
        "Volume": pd.to_numeric(df[volume_col], errors="coerce").fillna(0).astype("int64") if volume_col else 0,
    })

    out_df = out_df.dropna(subset=["Open", "High", "Low", "Close"])
    out_df = out_df.sort_values(["Date", "Time"]).drop_duplicates(subset=["Date", "Time"], keep="last")

    if out_df.empty:
        raise RuntimeError("No valid OHLC rows after normalization.")

    processed_dir = Path(cfg["output"]["processed_dir"])
    mt4_csv_dir = Path(cfg["output"]["mt4_csv_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    mt4_csv_dir.mkdir(parents=True, exist_ok=True)

    symbol = cfg["output"]["symbol"]

    processed_csv = processed_dir / f"{symbol}_D1_ohlc.csv"
    out_df.to_csv(processed_csv, index=False, encoding="utf-8-sig")

    # MT4-friendly CSV: Date,Time,Open,High,Low,Close,Volume
    mt4_csv = mt4_csv_dir / f"{symbol}_D1.csv"
    out_df.to_csv(mt4_csv, index=False, header=True, encoding="utf-8")

    logging.info("Raw CSV: %s", raw_csv)
    logging.info("Used columns: Date=%s Open=%s High=%s Low=%s Close=%s Volume=%s",
                 date_col, open_col, high_col, low_col, close_col, volume_col)
    logging.info("Saved processed CSV: %s", processed_csv)
    logging.info("Saved MT4 CSV: %s", mt4_csv)
    logging.info("Rows: %d", len(out_df))


if __name__ == "__main__":
    main()
