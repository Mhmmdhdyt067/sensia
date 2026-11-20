from pathlib import Path

LABELS = ["negatif", "netral", "positif"]
SEED = 42
MAX_LEN = 100
VOCAB_SIZE = 10000
MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
