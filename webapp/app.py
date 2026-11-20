import json
import sys
from pathlib import Path

if __package__ in (None, ""):  # `python webapp/app.py` puts webapp/ on sys.path, not the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

from sensia.config import LABELS, MAX_LEN, MODEL_DIR
from sensia.preprocess import clean_text

app = Flask(__name__)
METRICS_PATH = Path(__file__).with_name("metrics.json")


def load_artifacts(model_dir: Path = MODEL_DIR):
    model_dir = Path(model_dir)
    paths = {name: model_dir / name for name in ("sensia_bilstm.keras", "tokenizer.json", "label_map.json")}
    if not all(p.exists() for p in paths.values()):
        raise FileNotFoundError(
            f"Artefak model tidak ditemukan di {model_dir}. Jalankan notebook sensia_bilstm.ipynb dulu untuk menghasilkannya."
        )
    model = load_model(paths["sensia_bilstm.keras"])
    tokenizer = tokenizer_from_json(paths["tokenizer.json"].read_text())
    label_map = json.loads(paths["label_map.json"].read_text())
    if [label_map[str(i)] for i in range(len(LABELS))] != LABELS:
        raise ValueError(f"label_map.json tidak cocok dengan LABELS: {label_map}")
    return model, tokenizer, label_map


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
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    if len(text) < 3:
        return jsonify(error="Teks minimal 3 karakter."), 400
    if len(text) > 500:
        return jsonify(error="Teks maksimal 500 karakter."), 400

    clean = clean_text(text)
    if not clean:
        return jsonify(error="Teks tidak mengandung kata yang bisa dianalisis."), 400

    seq = pad_sequences(tokenizer.texts_to_sequences([clean]), maxlen=MAX_LEN, padding="post", truncating="post")
    probs = model.predict(seq, verbose=0)[0]
    best = int(probs.argmax())
    return jsonify(
        label=LABELS[best],
        confidence=round(float(probs[best]), 4),
        scores={label: round(float(p), 4) for label, p in zip(LABELS, probs)},
    )


if __name__ == "__main__":
    app.run(debug=True)
