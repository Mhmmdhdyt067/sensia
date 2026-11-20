import re

import pandas as pd

from sensia.config import LABELS

COLUMNS = ["text", "platform", "kata_kunci", "tanggal", "label"]
PLATFORMS = {"x", "threads"}

_PROMO = re.compile(r"promo|judi|slot|gacor|pinjol|casino|betting", re.IGNORECASE)
_NON_ALNUM = re.compile(r"[^a-z0-9]")


def validate_labeled(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"kolom wajib tidak ada: {', '.join(missing)}")

    df = df[COLUMNS].copy()

    null = df.isna().any()
    if null.any():
        raise ValueError(f"nilai kosong pada kolom: {', '.join(null[null].index)}")

    df["text"] = df["text"].astype(str)
    short = df["text"].str.len() < 5
    if short.any():
        raise ValueError(f"text terlalu pendek pada baris {list(df.index[short])[:5]}")

    bad_platform = ~df["platform"].isin(PLATFORMS)
    if bad_platform.any():
        raise ValueError(f"platform tidak dikenal pada baris {list(df.index[bad_platform])[:5]}")

    bad_label = ~df["label"].isin(LABELS)
    if bad_label.any():
        raise ValueError(f"label tidak dikenal pada baris {list(df.index[bad_label])[:5]}")

    bad_date = pd.to_datetime(df["tanggal"], format="%Y-%m-%d", errors="coerce").isna()
    if bad_date.any():
        raise ValueError(f"tanggal tidak valid (harus YYYY-MM-DD) pada baris {list(df.index[bad_date])[:5]}")

    return df


def dedupe_labeled(df: pd.DataFrame) -> pd.DataFrame:
    key = df["text"].astype(str).str.lower().map(lambda s: _NON_ALNUM.sub("", s))
    return df[~key.duplicated()].reset_index(drop=True)


def strip_ui_noise(df: pd.DataFrame) -> pd.DataFrame:
    """Remove scraped UI artefacts (date prefix, "Translate", trailing slash) from `text`."""
    df = df.copy()
    text = df["text"].astype(str).str.replace(r"^\d{2}/\d{2}/\d{2}\s+", "", regex=True)
    for _ in range(2):
        text = text.str.replace(r"\s*(?:Translate|/)\s*$", "", regex=True)
    df["text"] = text.str.strip()
    return df


def screen_raw(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    text = df["text"].astype(str)
    keep = (text.str.split().str.len() >= 5) & ~text.str.contains(_PROMO, na=False)
    return dedupe_labeled(df[keep])
