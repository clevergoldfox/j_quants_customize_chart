import argparse
import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    terminal_data_path = cfg.get("mt4", {}).get("terminal_data_path", "")
    terminal = Path(terminal_data_path)
    terminal_text = str(terminal).replace("\\", "/")

    if (
        not terminal_data_path
        or "YOUR_USER" in terminal_text
        or "YOUR_TERMINAL_ID" in terminal_text
        or not terminal.exists()
    ):
        print("MT4 terminal_data_path is not configured yet.")
        print(
            "Open MT4 > File > Open Data Folder, then set that path in config/config.json."
        )
        return 0

    scripts_subdir = cfg.get("mt4", {}).get("scripts_subdir", "MQL4/Scripts")
    indicators_subdir = cfg.get("mt4", {}).get("indicators_subdir", "MQL4/Indicators")
    pairs = [
        (Path("mt4/MQL4/Scripts"), terminal / scripts_subdir),
        (Path("mt4/MQL4/Indicators"), terminal / indicators_subdir),
    ]

    copied_count = 0
    for src_dir, dst_dir in pairs:
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src in src_dir.glob("*.mq4"):
            dst = dst_dir / src.name
            shutil.copy2(src, dst)
            print(f"Copied {src} -> {dst}")
            copied_count += 1

    if copied_count == 0:
        print("No MQ4 files found to copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
