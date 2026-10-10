"""G03: can observable pre-call features predict when JEV-9B is sufficient?

Policies route each item to JEV-9B (System 1) or to one frontier. Rules are fit on
training families/templates and evaluated on held-out ones (leave-one-family-out
and unseen-template splits). Baselines: always-X, length-only, family lookup,
JEV-9B confidence gate, and the (unavailable) oracle.
"""
from __future__ import annotations

import math
import re

import numpy as np

from .canonical import Task


def features(task: Task) -> dict:
    ev = task.evidence
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n", ev) if s.strip()]
    low = (task.evidence + " " + task.question).lower()
    return {
        "log_chars": math.log(len(ev) + len(task.question) + 1),
        "n_choices": len(task.choices),
        "n_sentences": len(sents),
        "conditionals": len(re.findall(r"\b(if|then|every|everyone|all|whoever|unless)\b", low)),
        "negations": len(re.findall(r"\b(not|no|never|none|neither|nor)\b", low)),
        "quantifiers": len(re.findall(r"\b(some|any|each|either|only)\b", low)),
        "digits": len(re.findall(r"\d", low)),
    }


FEATURES = ["log_chars", "n_choices", "n_sentences", "conditionals", "negations", "quantifiers", "digits"]


def fit_logistic(X: np.ndarray, y: np.ndarray, l2: float = 1.0, iters: int = 100) -> np.ndarray:
    """L2-regularised logistic regression by Newton's method (intercept unpenalised)."""
    X1 = np.hstack([np.ones((len(X), 1)), X])
    w = np.zeros(X1.shape[1])
    R = np.eye(X1.shape[1]) * l2
    R[0, 0] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X1 @ w))
        g = X1.T @ (p - y) + R @ w
        H = X1.T @ (X1 * (p * (1 - p))[:, None]) + R + 1e-9 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def predict(w, X):
    return 1 / (1 + np.exp(-(np.hstack([np.ones((len(X), 1)), X]) @ w)))


def _standardise(train, test):
    mu, sd = train.mean(0), train.std(0)
    sd[sd == 0] = 1
    return (train - mu) / sd, (test - mu) / sd


def evaluate_policies(train: list[dict], test: list[dict], tolerated_loss: float = 0.02) -> dict:
    """Each row: {'f': feature dict, 'family', 'conf': JEV max prob, 'jev': 0/1, 'front': 0/1,
    'cost_jev', 'cost_front'}. Thresholds are chosen on train only: route to JEV-9B when the
    predicted P(JEV correct) - P(frontier correct) on train-calibrated scale exceeds -tolerated_loss.
    """
    def mat(rows, cols):
        return np.array([[r["f"][c] for c in cols] for r in rows], dtype=float)

    out = {}

    def score(route_jev):
        acc = np.mean([r["jev"] if j else r["front"] for r, j in zip(test, route_jev)])
        cost = np.sum([r["cost_jev"] + (0 if j else r["cost_front"]) for r, j in zip(test, route_jev)])
        return {"accuracy": float(acc), "cost_usd": float(cost), "share_jev": float(np.mean(route_jev))}

    n = len(test)
    out["always_jev"] = score([True] * n)
    out["always_frontier"] = score([False] * n)
    out["oracle"] = score([bool(r["jev"] or not r["front"]) for r in test])

    # family lookup: per family, JEV-9B if its train accuracy is within tolerated_loss of the frontier
    fam = {}
    for r in train:
        fam.setdefault(r["family"], []).append(r)
    fam_choice = {k: np.mean([r["jev"] for r in v]) >= np.mean([r["front"] for r in v]) - tolerated_loss for k, v in fam.items()}
    out["family_lookup"] = score([fam_choice.get(r["family"], False) for r in test])  # unseen family -> frontier

    def gain_rule(cols, extra=None):
        Xtr, Xte = mat(train, cols), mat(test, cols)
        if extra:
            Xtr = np.hstack([Xtr, np.array([[r[e] for e in extra] for r in train])])
            Xte = np.hstack([Xte, np.array([[r[e] for e in extra] for r in test])])
        Xtr, Xte = _standardise(Xtr, Xte)
        wj = fit_logistic(Xtr, np.array([r["jev"] for r in train], float))
        wf = fit_logistic(Xtr, np.array([r["front"] for r in train], float))
        return list(predict(wj, Xte) - predict(wf, Xte) >= -tolerated_loss)

    out["length_only"] = score(gain_rule(["log_chars"]))
    out["feature_rule"] = score(gain_rule(FEATURES))
    out["feature_rule+conf"] = score(gain_rule(FEATURES, ["conf"]))
    # confidence gate: smallest threshold whose train-routed accuracy stays within tolerated_loss of always-frontier
    best = 1.01
    base = np.mean([r["front"] for r in train])
    for t in np.linspace(0.3, 1.0, 71):
        acc = np.mean([r["jev"] if r["conf"] >= t else r["front"] for r in train])
        if acc >= base - tolerated_loss:
            best = t
            break
    out["confidence_gate"] = {**score([r["conf"] >= best for r in test]), "threshold": float(best)}
    return out
