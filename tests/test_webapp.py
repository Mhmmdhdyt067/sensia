import pytest

from sensia.config import LABELS
from webapp.app import app, load_artifacts


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_landing_page_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"SenSia" in r.data


def test_predict_returns_three_scores(client):
    r = client.post("/predict", json={"text": "ihsg anjlok parah hari ini"})
    body = r.get_json()
    assert r.status_code == 200
    assert body["label"] in LABELS
    assert 0.0 <= body["confidence"] <= 1.0
    assert sorted(body["scores"]) == sorted(LABELS)


def test_predict_rejects_empty(client):
    assert client.post("/predict", json={"text": "  "}).status_code == 400


def test_predict_rejects_too_short(client):
    assert client.post("/predict", json={"text": "ok"}).status_code == 400


def test_predict_rejects_over_limit(client):
    assert client.post("/predict", json={"text": "a" * 501}).status_code == 400


def test_predict_accepts_max_length(client):
    assert client.post("/predict", json={"text": "saham " * 83}).status_code == 200


def test_predict_rejects_text_that_cleans_to_nothing(client):
    r = client.post("/predict", json={"text": "😭😭🚀🔥"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_label_map_must_match_labels():
    _, _, label_map = load_artifacts()
    assert [label_map[str(i)] for i in range(3)] == LABELS


def test_load_artifacts_missing_model_message(tmp_path):
    with pytest.raises(FileNotFoundError, match="notebook"):
        load_artifacts(tmp_path)


def test_predict_rejects_punctuation_only(client):
    assert client.post("/predict", json={"text": ".,.,."}).status_code == 400


def test_predict_rejects_non_string_text(client):
    assert client.post("/predict", json={"text": None}).status_code == 400
    assert client.post("/predict", json={"text": {"a": 1}}).status_code == 400


def test_predict_rejects_non_object_body(client):
    assert client.post("/predict", json=42).status_code == 400
