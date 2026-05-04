import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

from jquants_client import JQuantsClient


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"fetch_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg = load_config(args.config)
    log_dir = Path(cfg["output"]["log_dir"])
    setup_logging(log_dir)

    code = cfg["stock"]["code"]
    from_ = cfg["stock"].get("from") or None
    to = cfg["stock"].get("to") or None

    client = JQuantsClient(
        api_key=cfg["jquants"]["api_key"],
        base_url=cfg["jquants"].get("base_url", "https://api.jquants.com"),
        api_version=cfg["jquants"].get("api_version", "v2"),
    )

    logging.info("Fetching daily quotes: code=%s from=%s to=%s", code, from_, to)
    rows = client.get_daily_quotes(code=code, from_=from_, to=to)

    if not rows:
        raise RuntimeError("No rows returned from J-Quants API.")

    raw_dir = Path(cfg["output"]["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{code}_daily_quotes_raw.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    csv_out = raw_dir / f"{code}_daily_quotes_raw.csv"
    pd.DataFrame(rows).to_csv(csv_out, index=False, encoding="utf-8-sig")

    logging.info("Saved raw JSON: %s", out)
    logging.info("Saved raw CSV: %s", csv_out)


if __name__ == "__main__":
    main()
