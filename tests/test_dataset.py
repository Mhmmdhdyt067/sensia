import pandas as pd
import pytest

from sensia.dataset import COLUMNS, dedupe_labeled, screen_raw, validate_labeled


def make_df(**overrides):
    rows = [
        {"text": "ihsg anjlok lagi parah banget hari ini",
         "platform": "x", "kata_kunci": "ihsg anjlok",
         "tanggal": "2026-11-14", "label": "negatif"},
        {"text": "waktunya akumulasi bbca murah banget sekarang",
         "platform": "threads", "kata_kunci": "bbca",
         "tanggal": "2026-11-14", "label": "positif"},
        {"text": "ihsg ditutup di 6812 turun satu persen hari ini",
         "platform": "x", "kata_kunci": "ihsg hari ini",
         "tanggal": "2026-11-13", "label": "netral"},
    ]
    rows[0].update(overrides)
    return pd.DataFrame(rows)[COLUMNS]


def test_valid_frame_passes():
    assert len(validate_labeled(make_df())) == 3


def test_missing_column_raises():
    with pytest.raises(ValueError, match="label"):
        validate_labeled(make_df().drop(columns=["label"]))


def test_invalid_label_raises():
    with pytest.raises(ValueError, match="label"):
        validate_labeled(make_df(label="positif banget"))


def test_null_text_raises():
    with pytest.raises(ValueError, match="text"):
        validate_labeled(make_df(text=None))


def test_bad_date_raises():
    with pytest.raises(ValueError, match="tanggal"):
        validate_labeled(make_df(tanggal="14/11/2026"))


def test_unknown_platform_raises():
    with pytest.raises(ValueError, match="platform"):
        validate_labeled(make_df(platform="facebook"))


def test_dedupe_collapses_text_differing_only_in_case_and_symbols():
    df = pd.concat([make_df(), make_df(text="IHSG ANJLOK!!! lagi parah banget hari ini")])
    assert len(dedupe_labeled(df)) == 3


def test_screen_raw_drops_promo_and_short_rows():
    df = pd.DataFrame({
        "text": ["slot gacor promo judi online hari ini cair",
                 "mantap",
                 "ihsg anjlok lagi parah banget hari ini"],
        "platform": ["x", "x", "x"],
        "kata_kunci": ["k", "k", "k"],
        "tanggal": ["2026-11-14"] * 3,
    })
    assert len(screen_raw(df)) == 1
