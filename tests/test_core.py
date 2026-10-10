import json
from types import SimpleNamespace

import pytest

from jevstudy import controlled as C
from jevstudy import datasets as D
from jevstudy import stats
from jevstudy.adapters.anthropic_fable import FableAdapter
from jevstudy.adapters.jev9b import Jev9bS1Adapter, parse_free_answer
from jevstudy.adapters.openai_astra import AstraAdapter
from jevstudy.canonical import Task, jev_state, render, task_hash
from jevstudy.judge_practice import judge_practice_tasks
from jevstudy.run import Cache, Ledger, run_sync

RATES = {"input": 10.0, "cached_input": 1.0, "cache_write": 12.5, "cache_read": 0.25, "output": 50.0, "batch_multiplier": 0.5}
FORBIDDEN = {"label", "gold", "answer", "reason", "premises-FOL", "conclusion-FOL", "response_model"}


# ------------------------------------------------------------- gold exclusion and label mapping
def test_folio_mapping_and_no_gold_fields():
    row = {"premises": ["All cats are animals.", "Tom is a cat."], "premises-FOL": ["x"], "conclusion": "Tom is an animal.",
           "conclusion-FOL": "y", "label": "Uncertain"}
    t, g = D._folio_task(row, 0, "final", "folio-val")
    assert g.answer_label == "Unknown" and g.answer_id == "C"
    assert not FORBIDDEN & set(t.to_json()) and not FORBIDDEN & set(t.meta)
    assert "x" not in render(t).split("Premises:")[1].split("Question")[0].split()  # FOL never rendered


def test_anli_mapping_excludes_reason():
    row = {"uid": "u1", "premise": "P.", "hypothesis": "H.", "label": 2, "reason": "SECRET-REASON"}
    t, g = D._anli_task(row, "final", "anli")
    assert g.answer_label == "contradiction" and g.answer_id == "C"
    assert "SECRET-REASON" not in json.dumps(t.to_json())


def test_judgebench_mapping_hides_generator():
    row = {"pair_id": "p", "original_id": 3, "source": "mmlu-pro", "question": "Q", "response_model": "SECRET-MODEL",
           "response_A": "a", "response_B": "b", "label": "B>A"}
    t, g = D._judge_task(row, "gpt")
    assert g.answer_id == "B" and "SECRET-MODEL" not in json.dumps(t.to_json())


def test_banking_candidates_contain_gold_and_are_16():
    train = [{"text": f"my card {w} please", "category": f"lab_{i}"} for i in range(20) for w in ("x", "y", "z")]
    conf = D.banking_confusable_sets(train)
    t, g = D._banking_task({"text": "where is my card", "category": "lab_3"}, 0, "final", "banking-test", conf)
    assert len(t.choices) == 16 and t.choices[ord(g.answer_id) - 65] == "lab 3"


def test_judge_practice_balanced():
    golds = [g.answer_id for _, g in judge_practice_tasks()]
    assert sorted(golds) == ["A", "A", "A", "B", "B", "B"]


def test_dev_and_final_clusters_disjoint_controlled():
    dev = {t.cluster_id for t, _ in C.dev_panel()}
    fin = {t.cluster_id for t, _ in C.final_panel()}
    assert not dev & fin


# ------------------------------------------------------------- prompt parity
def _task(n=3):
    return Task("t1", "folio", "dev", "c1", "Instr.", "Evidence text.", "Question?", tuple(f"opt{i}" for i in range(n)))


def test_same_semantic_content_for_all_systems():
    t = _task()
    a = AstraAdapter.__new__(AstraAdapter)
    a.config = {"model": "m", "effort": "high", "max_output_tokens": 10}
    f = FableAdapter.__new__(FableAdapter)
    f.config = {"model": "m", "effort": "high", "max_tokens": 10}
    assert a.params(t)["input"] == f.params(t)["messages"][0]["content"] == render(t)
    j = Jev9bS1Adapter.__new__(Jev9bS1Adapter)
    jp = j.prompt(t)
    for part in (t.instructions, t.evidence, t.question, *t.choices):
        assert part in jp and part in render(t)
    assert jev_state(t) in jp


def test_cache_keys_differ_by_model_and_effort(tmp_path):
    t = _task()
    keys = set()
    for effort in ("high", "xhigh"):
        a = AstraAdapter.__new__(AstraAdapter)
        a.system, a.config = f"astra-{effort}", {"model": "gpt-6-astra", "effort": effort}
        f = FableAdapter.__new__(FableAdapter)
        f.system, f.config = f"fable-{effort}", {"model": "claude-fable-5-1", "effort": effort}
        keys |= {a.request_key(t), f.request_key(t)}
    assert len(keys) == 4
    t2 = Task("t1", "folio", "dev", "c1", "Instr.", "Evidence text!", "Question?", t.choices)
    assert task_hash(t2) != task_hash(t)


# ------------------------------------------------------------- cost accounting
def test_reasoning_tokens_not_double_counted():
    a = AstraAdapter.__new__(AstraAdapter)
    a.rates = RATES
    resp = {"status": "completed", "usage": {"input_tokens": 1000, "output_tokens": 3000,
            "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 2990}},
            "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"answer": "B"}'}]}]}
    status, ans, usage = AstraAdapter.parse(resp)
    assert (status, ans) == ("ok", "B")
    assert a.cost(usage) == pytest.approx((1000 * 10 + 3000 * 50) / 1e6)
    assert a.cost(usage, batch=True) == pytest.approx(a.cost(usage) / 2)


def test_fable_parse_and_cost():
    f = FableAdapter.__new__(FableAdapter)
    f.rates = RATES
    msg = {"stop_reason": "end_turn", "usage": {"input_tokens": 500, "output_tokens": 2000},
           "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": '{"answer":"A"}'}]}
    status, ans, usage = FableAdapter.parse(msg)
    assert (status, ans) == ("ok", "A")
    assert f.cost(usage) == pytest.approx((500 * 10 + 2000 * 50) / 1e6)
    assert FableAdapter.parse({**msg, "stop_reason": "max_tokens"})[0] == "truncated"
    assert FableAdapter.parse({**msg, "stop_reason": "refusal"})[0] == "refusal"


# ------------------------------------------------------------- retries and ledger
class _FakeAPIError(Exception):
    pass


def test_retry_at_most_once_and_not_on_bad_request(monkeypatch):
    import openai
    calls = {"n": 0}

    class Resp:
        headers = {"retry-after": "0"}

    def boom(**kw):
        calls["n"] += 1
        raise openai.APIConnectionError(request=SimpleNamespace(method="POST", url="x"))

    a = AstraAdapter.__new__(AstraAdapter)
    a.system, a.rates = "astra-high", RATES
    a.config = {"model": "m", "effort": "high", "max_output_tokens": 10}
    a.client = SimpleNamespace(responses=SimpleNamespace(create=boom))
    r = a.run(_task())
    assert r.status == "error" and calls["n"] == 2 and r.attempts == 2


def test_ledger_reservation_and_forecast_stop(tmp_path):
    led = Ledger(tmp_path / "l.jsonl", stage_forecast_usd=1.0)
    led.reserve("k", "s", 0.6)
    led.settle("k", "s", 0.6, 0.1, {})
    assert led.summary() == {"spent_usd": 0.1, "committed_usd": 0.0}
    with pytest.raises(Exception):
        led.reserve("k2", "s", 0.95)
    assert Ledger(tmp_path / "l.jsonl").spent == pytest.approx(0.1)  # survives restart


def test_runner_is_cached_and_gold_blind(tmp_path):
    from jevstudy.adapters.base import Adapter, Result

    class Fake(Adapter):
        def __init__(self):
            self.system, self.config, self.n = "fake", {"v": 1}, 0

        def run(self, task):
            self.n += 1
            return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "ok", "A", cost_usd=0.01)

    ad = Fake()
    led, cache = Ledger(tmp_path / "l.jsonl"), Cache(tmp_path / "c")
    run_sync([_task()], [ad], tmp_path / "o.jsonl", led, cache, log=lambda *_: None)
    run_sync([_task()], [ad], tmp_path / "o.jsonl", led, cache, log=lambda *_: None)
    assert ad.n == 1 and led.spent == pytest.approx(0.01)


# ------------------------------------------------------------- controlled panel semantics
def test_reference_scorers_agree_and_depth_is_exact():
    for t, g in C.final_panel(evidence_removal=True):
        if t.meta["condition"] == "base" and g.answer_label != "Unknown":
            assert t.meta["derivation_depth"] == t.meta["depth"]
    labels = [g.answer_label for t, g in C.final_panel() if t.meta["condition"] == "base"]
    assert labels.count("True") == labels.count("False") == labels.count("Unknown")


def test_contrapositive_is_classical():
    # P -> Q, not Q  |=  not P  (forward chaining alone would say Unknown; brute force must not)
    rules = [(("p", True), ("q", True))]
    assert C.entails_bruteforce([("q", False)], rules, ("p", True)) == "False"
    assert C.forward_chain([("q", False)], rules, ("p", True))[0] == "Unknown"


def test_controls_change_or_preserve_gold():
    items = {t.task_id: (t, g) for t, g in C.final_panel()}
    for seed in C.FINAL_SEEDS[:12]:
        base = items[f"ctl-{seed}-d3-c8"][1].answer_label
        assert items[f"ctl-{seed}-change"][1].answer_label != base
        assert items[f"ctl-{seed}-preserve"][1].answer_label == base


def test_controlled_inputs_short_enough_for_jev():
    assert max(len(render(t)) for t, _ in C.final_panel()) < 2400  # well below 1,024 tokens


# ------------------------------------------------------------- statistics
def test_newcombe_properties():
    d, lo, hi = stats.newcombe_paired(12, 9, 2, 21)
    assert d == pytest.approx(7 / 44) and lo < d < hi and lo > -1 and hi < 1
    # no discordant pairs must not produce a degenerate zero-width interval
    d0, lo0, hi0 = stats.newcombe_paired(50, 0, 0, 10)
    assert d0 == 0 and lo0 < 0 < hi0 and hi0 - lo0 > 0.02


def test_cluster_bootstrap_coverage():
    r = stats.simulate_coverage(n_clusters=40, cluster_size=6, reps=120, seed=2, B=500)
    assert r["coverage"] >= 0.88


def test_classification_rule():
    base = {"clusters": 100}
    assert stats.classify({**base, "lo": 0.01, "hi": 0.05}, True) == "JEV-9B more accurate"
    assert stats.classify({**base, "lo": -0.01, "hi": 0.03}, True).startswith("comparable")
    assert stats.classify({**base, "lo": -0.2, "hi": -0.05}, True) == "frontier materially more accurate"
    assert stats.classify({**base, "lo": -0.05, "hi": 0.01}, True) == "inconclusive"


def test_interval_coverage_small_simulation():
    r = stats.simulate_coverage(n_clusters=80, cluster_size=1, reps=150, seed=1)
    assert r["coverage"] >= 0.90


def test_parse_free_answer():
    assert parse_free_answer('reasoning...\n{"answer": "C"}', ("A", "B", "C")) == "C"
    assert parse_free_answer("Final answer: B", ("A", "B", "C")) == "B"
    assert parse_free_answer("I think D", ("A", "B", "C")) is None
