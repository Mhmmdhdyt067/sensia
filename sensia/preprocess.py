import re

SLANG = {
    "udah": "sudah", "sdh": "sudah", "blm": "belum", "gak": "tidak",
    "ga": "tidak", "nggak": "tidak", "gk": "tidak", "tdk": "tidak",
    "bgt": "banget", "bngt": "banget", "yg": "yang", "dgn": "dengan",
    "utk": "untuk", "krn": "karena", "krna": "karena", "jg": "juga",
    "aja": "saja", "bkn": "bukan", "lg": "lagi", "msh": "masih",
    "hrs": "harus", "bs": "bisa", "dpt": "dapat", "sy": "saya",
    "gw": "saya", "gue": "saya", "ane": "saya", "lu": "kamu",
    "lo": "kamu", "emg": "memang", "mmg": "memang", "pdhl": "padahal",
    "sbnrnya": "sebenarnya", "skrg": "sekarang", "tgl": "tanggal",
    "hr": "hari", "thn": "tahun", "bln": "bulan", "cuan": "untung",
    "boncos": "rugi", "nyangkut": "terjebak", "banting": "jual",
    "hijau": "naik", "merah": "turun",
}

_URL = re.compile(r"https?://\S+|www\.\S+")
_MENTION = re.compile(r"@\w+")
_HASHTAG = re.compile(r"#")
_NOT_ALLOWED = re.compile(r"[^a-z0-9\s.,]")
_SPACES = re.compile(r"\s+")

_SLANG_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, SLANG), key=len, reverse=True)) + r")\b"
)


def basic_clean(text: str) -> str:
    text = text.lower()
    text = _URL.sub(" ", text)
    text = _MENTION.sub(" ", text)
    text = _HASHTAG.sub("", text)
    text = _NOT_ALLOWED.sub("", text)
    return _SPACES.sub(" ", text).strip()


def normalize_slang(text: str) -> str:
    return _SLANG_PATTERN.sub(lambda m: SLANG[m.group(0)], text)


def clean_text(text: str) -> str:
    return normalize_slang(basic_clean(text))
