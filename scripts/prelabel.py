"""Bangun workbook pelabelan dari CSV mentah.

Default: `data/labeled/sensia_verifikasi.xlsx` — kolom `label` kosong untuk diisi
manusia, `label_saran` hanya alat bantu.

`--draft`: `data/labeled/sensia_labeled.xlsx` — `label` diisi dari `label_saran`
supaya notebook bisa dilatih. Label ini **belum** diverifikasi manusia.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sensia.dataset import COLUMNS, screen_raw, strip_ui_noise  # noqa: E402

RAW = ROOT / "data/raw/sensia_raw.csv"
OUT = ROOT / "data/labeled/sensia_verifikasi.xlsx"
DRAFT = ROOT / "data/labeled/sensia_labeled.xlsx"

NEG = r"\b(anjlok|turun|rugi|boncos|arb|cut ?loss|gorengan|kapok|ambles|jemput|terjun|melemah|hancur|nyangkut|buntung)\b"
POS = r"\b(naik|untung|cuan|beli|akumulasi|rebound|murah|menguat|hijau|profit|untung|gaspol|melonjak)\b"


def suggest(text: str) -> str:
    t = " " + re.sub(r"[^a-z0-9 ]", " ", text.lower()) + " "
    neg, pos = bool(re.search(NEG, t)), bool(re.search(POS, t))
    if neg and not pos:
        return "negatif"
    if pos and not neg:
        return "positif"
    return "netral"


def main() -> int:
    draft = "--draft" in sys.argv
    if not RAW.exists():
        print(f"tidak ada {RAW}", file=sys.stderr)
        return 1

    df = screen_raw(strip_ui_noise(pd.read_csv(RAW)))[COLUMNS[:-1]]
    df["label_saran"] = df["text"].map(suggest)
    df["label"] = df["label_saran"] if draft else ""
    df = df[COLUMNS + ["label_saran"]]

    out = DRAFT if draft else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as xl:
        df.to_excel(xl, index=False, sheet_name="labeling")
        ws = xl.sheets["labeling"]
        for col, width in zip("ABCDEF", (100, 10, 16, 12, 12, 13)):
            ws.column_dimensions[col].width = width
        ws.freeze_panes = "A2"

    print(f"{len(df)} baris -> {out.relative_to(ROOT)}")
    print(df["label_saran"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
