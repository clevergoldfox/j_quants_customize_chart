import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from copy import deepcopy


def run(cmd):
    print(">", " ".join(str(x) for x in cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(str(x) for x in cmd)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--install", action="store_true", help="Copy generated CSV files to MT4 MQL4/Files.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    base_cfg_path = root / args.config
    base_cfg = json.loads(base_cfg_path.read_text(encoding="utf-8"))

    stocks = base_cfg.get("stocks")
    if not stocks:
        stock = base_cfg.get("stock", {})
        stocks = [{
            "code": stock.get("code"),
            "symbol": base_cfg.get("output", {}).get("symbol", f"JP{stock.get('code', '')[:4]}"),
            "name": stock.get("name", "")
        }]

    tmp_dir = root / "config" / "_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    for s in stocks:
        code = str(s["code"]).strip()
        symbol = str(s.get("symbol") or f"JP{code[:4]}").strip()
        name = str(s.get("name") or "").strip()

        print("\n" + "=" * 70)
        print(f"Updating {symbol} / {code} / {name}")
        print("=" * 70)

        cfg = deepcopy(base_cfg)
        cfg["stock"]["code"] = code
        cfg["stock"]["name"] = name
        cfg["output"]["symbol"] = symbol

        tmp_cfg = tmp_dir / f"config_{symbol}.json"
        tmp_cfg.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

        try:
            run([sys.executable, str(root / "scripts" / "fetch_jquants_v2.py"), "--config", str(tmp_cfg)])
            run([sys.executable, str(root / "scripts" / "normalize_ohlc.py"), "--config", str(tmp_cfg)])
            if args.install:
                run([sys.executable, str(root / "scripts" / "install_to_mt4.py"), "--config", str(tmp_cfg)])
        except Exception as e:
            errors.append((symbol, code, str(e)))
            print(f"[ERROR] {symbol} failed: {e}")

    if errors:
        print("\nFAILED STOCKS:")
        for symbol, code, err in errors:
            print(f"- {symbol} {code}: {err}")
        raise SystemExit(1)

    print("\nAll stocks updated successfully.")


if __name__ == "__main__":
    main()
