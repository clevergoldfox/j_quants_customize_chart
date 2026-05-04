import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    symbol = cfg["output"]["symbol"]
    mt4_csv = Path(cfg["output"]["mt4_csv_dir"]) / f"{symbol}_D1.csv"

    terminal_data_path = Path(cfg["mt4"]["terminal_data_path"])
    files_subdir = cfg["mt4"].get("files_subdir", "MQL4/Files")
    dest_dir = terminal_data_path / files_subdir
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not mt4_csv.exists():
        raise FileNotFoundError(f"MT4 CSV not found: {mt4_csv}")

    dest = dest_dir / mt4_csv.name
    shutil.copy2(mt4_csv, dest)

    print(f"Copied {mt4_csv} -> {dest}")


if __name__ == "__main__":
    main()
