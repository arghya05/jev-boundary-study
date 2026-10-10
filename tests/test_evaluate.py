from jevstudy import evaluate
from jevstudy.adapters.base import Result
from jevstudy.canonical import task_hash


class FakeJev:
    """Deterministic stand-in for JevClient: confident 'true' unless the response mentions 'Sydney'."""

    def decide(self, question, state="", options=None, kind="choice"):
        if kind == "noul":
            p = 0.05 if "Sydney" in state else 0.95
            return {"false": 1 - p, "true": p}
        if kind == "score":
            return {str(i): (0.8 if i == 4 else 0.04) for i in range(6)}
        return {options[0]: 0.55, options[1]: 0.45}


class FakeFrontier:
    system = "astra-high"

    def __init__(self):
        self.calls = 0

    def run(self, task):
        self.calls += 1
        return Result(self.system, task.task_id, task_hash(task), "k", "ok", "B", cost_usd=0.01)


def test_pointwise_agreement_and_auroc():
    rows = [{"id": "1", "question": "q", "response": "fine", "label": True},
            {"id": "2", "question": "q", "response": "Sydney", "label": False}]
    out, s = evaluate.judge(rows, "pointwise", FakeJev())
    assert s["agreement"] == 1.0 and s["jev_auroc"] == 1.0 and s["escalated"] == 0


def test_low_confidence_pairwise_escalates_and_is_billed():
    fr = FakeFrontier()
    rows = [{"id": "1", "question": "q", "response_a": "a", "response_b": "b", "label": "B"}]
    out, s = evaluate.judge(rows, "pairwise", FakeJev(), escalate=fr, threshold=0.9)
    assert fr.calls == 1 and out[0]["judge"] == "astra-high" and out[0]["verdict"] == "B"
    assert s["agreement"] == 1.0 and s["cost_usd"] == 0.01


def test_score_mode_expected_value():
    out, s = evaluate.judge([{"id": "1", "question": "q", "response": "r", "label": 4}], "score", FakeJev())
    assert out[0]["verdict"] == 4 and s["mae"] == 0


def test_custom_report_and_gate(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(
        f'{{"id": "{i}", "question": "q{i}", "choices": ["x", "y"], "answer": "{"x" if i % 2 else "y"}"}}' for i in range(30)))
    pairs = evaluate.custom_tasks(p)
    res = []
    for t, g in pairs:
        conf = 0.95 if int(t.task_id) % 3 else 0.6
        jev_ans = g.answer_id if conf > 0.9 else ("A" if g.answer_id == "B" else "B")
        res.append({"system": "jev9b-s1", "task_id": t.task_id, "status": "ok", "answer_id": jev_ans, "cost_usd": 0.0,
                    "distribution": {"A": conf, "B": 1 - conf}})
        res.append({"system": "astra-high", "task_id": t.task_id, "status": "ok", "answer_id": g.answer_id, "cost_usd": 0.01})
    rep = evaluate.custom_report(pairs, res)
    gate = {g["threshold"]: g for g in rep["jev9b-s1_vs_astra-high"]["confidence_gate"]}
    assert gate[0.9]["accuracy"] == 1.0 and 0 < gate[0.9]["share_escalated"] < 1
    assert rep["systems"]["astra-high"]["accuracy"] == 1.0
    assert (evaluate.write_report(rep, tmp_path / "out")).exists()
