import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from jevstudy import server  # noqa: E402


class FakeJev:
    def decide(self, question, state="", options=None, kind="choice"):
        if kind == "noul":
            return {"false": 0.2, "true": 0.8}
        if kind == "score":
            return {str(i): (0.75 if i == 3 else 0.05) for i in range(6)}
        # position bias: always prefers the first option slightly; content preference for "7 x 13"
        a_good = "7 x 13" in state.split("Response B:")[0]
        return {options[0]: 0.9 if a_good else 0.6, options[1]: 0.1 if a_good else 0.4}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(server, "_jev", FakeJev())
    monkeypatch.setenv("JUDGE_API_KEY", "k")
    return TestClient(server.app)


def test_auth_required(client):
    assert client.post("/v1/judge", json={"question": "q", "response": "r"}).status_code == 401


def test_judge_and_score(client):
    h = {"Authorization": "Bearer k"}
    r = client.post("/v1/judge", json={"question": "q", "response": "r"}, headers=h).json()
    assert r["verdict"] is True and abs(r["p_correct"] - 0.8) < 1e-9 and r["system"] == "jev9b"
    s = client.post("/v1/score", json={"question": "q", "response": "r"}, headers=h).json()
    assert s["score"] == 3


def test_compare_is_position_debiased(client):
    h = {"Authorization": "Bearer k"}
    body = {"question": "Is 91 prime?", "response_a": "No, 91 = 7 x 13.", "response_b": "Yes."}
    r1 = client.post("/v1/compare", json=body, headers=h).json()
    r2 = client.post("/v1/compare", json={**body, "response_a": body["response_b"], "response_b": body["response_a"]}, headers=h).json()
    assert r1["winner"] == "A" and r2["winner"] == "B"            # same verdict on content after swapping
    assert abs(r1["p_a_better"] - r2["p_b_better"]) < 1e-9          # exactly symmetric


def test_batch_and_escalation_validation(client):
    h = {"Authorization": "Bearer k"}
    r = client.post("/v1/batch", json={"mode": "decide", "items": [{"question": "q", "options": ["x", "y"]}]}, headers=h).json()
    assert len(r["results"]) == 1
    bad = client.post("/v1/decide", json={"question": "q", "options": ["x", "y"],
                                          "escalate": {"to": "astra", "threshold": 0.99}}, headers=h)
    assert bad.status_code == 400   # frontier escalation needs the caller's key
