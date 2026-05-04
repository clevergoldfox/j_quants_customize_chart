import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--install", action="store_true", help="Copy generated CSV into MT4 MQL4/Files.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    py = sys.executable

    run([py, str(root / "scripts" / "fetch_jquants_v2.py"), "--config", args.config])
    run([py, str(root / "scripts" / "normalize_ohlc.py"), "--config", args.config])

    if args.install:
        run([py, str(root / "scripts" / "install_to_mt4.py"), "--config", args.config])


if __name__ == "__main__":
    main()
