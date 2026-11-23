"""Ubah hasil verifikasi manusia (data/labeled/sensia_verifikasi.xlsx) jadi dataset final.

Baris yang kolom `label`-nya masih kosong dilewati, jadi Anda bisa menyimpan
progres setengah jalan. Output: data/labeled/sensia_labeled.xlsx lima kolom.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sensia.config import LABELS  # noqa: E402
from sensia.dataset import COLUMNS, dedupe_labeled, validate_labeled  # noqa: E402

SRC = ROOT / "data/labeled/sensia_verifikasi.xlsx"
OUT = ROOT / "data/labeled/sensia_labeled.xlsx"


def main() -> int:
    df = pd.read_excel(SRC)
    total = len(df)

    label = df["label"].astype("string").str.strip().str.lower()
    df = df[label.notna() & (label != "")].copy()
    df["label"] = label[label.notna() & (label != "")]
    if df.empty:
        print(f"belum ada baris berlabel di {SRC.name} (0 dari {total})", file=sys.stderr)
        return 1

    bad = sorted(set(df["label"]) - set(LABELS))
    if bad:
        print(f"label tidak dikenal: {bad}; pilihan: {LABELS}", file=sys.stderr)
        return 1

    df = dedupe_labeled(validate_labeled(df[COLUMNS]))
    df.to_excel(OUT, index=False)

    counts = df["label"].value_counts().reindex(LABELS, fill_value=0)
    print(f"{len(df)} baris terpakai dari {total} ({total - len(df)} kosong/duplikat) -> {OUT.relative_to(ROOT)}")
    print(counts.to_string())
    if counts.min() < 100:
        print(f"peringatan: kelas terkecil hanya {counts.min()} baris, metrik per kelas akan goyah", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
