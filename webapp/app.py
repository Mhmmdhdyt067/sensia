import json
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

LABELS = ["negatif", "netral", "positif"]
MAX_LEN = 100
MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
METRICS_PATH = Path(__file__).with_name("metrics.json")

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
_NOT_ALLOWED = re.compile(r"[^a-z0-9\s]")
_SPACES = re.compile(r"\s+")
_SLANG_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, SLANG), key=len, reverse=True)) + r")\b"
)


def basic_clean(text: str) -> str:
    text = str(text).lower()
    text = _URL.sub(" ", text)
    text = _MENTION.sub(" ", text)
    text = _HASHTAG.sub("", text)
    text = _NOT_ALLOWED.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def normalize_slang(text: str) -> str:
    return _SLANG_PATTERN.sub(lambda m: SLANG[m.group(0)], text)


def clean_text(text: str) -> str:
    return normalize_slang(basic_clean(text))


app = Flask(__name__, template_folder=".")


def _check_label_map(label_map: dict) -> None:
    if label_map != {str(i): label for i, label in enumerate(LABELS)}:
        raise ValueError(f"label_map.json tidak cocok dengan LABELS: {label_map}")


def load_artifacts(model_dir: Path = MODEL_DIR):
    model_dir = Path(model_dir)
    paths = {
        name: model_dir / name
        for name in ("sensia_bilstm.keras", "tokenizer.json", "label_map.json")
    }
    if not all(p.exists() for p in paths.values()):
        raise FileNotFoundError(
            f"Artefak model tidak ditemukan di {model_dir}. "
            "Jalankan notebook sensia_bilstm.ipynb dulu untuk menghasilkannya."
        )
    loaded_model = load_model(paths["sensia_bilstm.keras"])
    loaded_tokenizer = tokenizer_from_json(paths["tokenizer.json"].read_text())
    loaded_label_map = json.loads(paths["label_map.json"].read_text())
    _check_label_map(loaded_label_map)
    return loaded_model, loaded_tokenizer, loaded_label_map


def load_metrics() -> dict:
    try:
        return json.loads(METRICS_PATH.read_text())
    except (OSError, ValueError):
        return {}


model, tokenizer, LABEL_MAP = load_artifacts()


@app.get("/")
def index():
    return render_template("index.html", metrics=load_metrics(), labels=LABELS)


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        return jsonify(error='Body harus JSON berbentuk {"text": string}.'), 400
    text = payload["text"].strip()
    if len(text) < 3:
        return jsonify(error="Teks minimal 3 karakter."), 400
    if len(text) > 500:
        return jsonify(error="Teks maksimal 500 karakter."), 400

    clean = clean_text(text)
    tokens = tokenizer.texts_to_sequences([clean])[0]
    if not tokens:
        return jsonify(error="Teks tidak mengandung kata yang bisa dianalisis."), 400

    seq = pad_sequences([tokens], maxlen=MAX_LEN, padding="post", truncating="post")
    probs = model.predict(seq, verbose=0)[0]
    best = int(probs.argmax())
    return jsonify(
        label=LABELS[best],
        confidence=round(float(probs[best]), 4),
        scores={label: round(float(p), 4) for label, p in zip(LABELS, probs)},
    )


if __name__ == "__main__":
    app.run(debug=True)
