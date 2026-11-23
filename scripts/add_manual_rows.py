"""Append transkripsi screenshot manual ke data/raw/sensia_manual.csv (dedupe saat merge)."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw/sensia_manual.csv"
COLS = ["text", "platform", "kata_kunci", "tanggal"]


def main() -> int:
    rows = json.load(sys.stdin)
    new = not OUT.exists()
    with OUT.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLS})
    print(f"+{len(rows)} -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
