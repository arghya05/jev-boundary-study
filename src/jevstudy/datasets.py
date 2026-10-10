"""Public dataset loading, pinned by source commit/URL and file SHA-256.

Inference objects (`Task`) never contain gold labels, ANLI `reason`, FOLIO
logical forms, or JudgeBench generator identity. Gold goes to a separate list.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import requests

from .canonical import LETTERS, Gold, Task, sha256
from .judge_practice import judge_practice_tasks

FOLIO_COMMIT = "5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d"
BANKING_COMMIT = "57ec275d8078af65b7731c2a98be812d844a6d6b"
SOURCES = {
    "folio_validation": f"https://raw.githubusercontent.com/Yale-LILY/FOLIO/{FOLIO_COMMIT}/data/v0.0/folio-validation.jsonl",
    "folio_train": f"https://raw.githubusercontent.com/Yale-LILY/FOLIO/{FOLIO_COMMIT}/data/v0.0/folio-train.jsonl",
    "banking_test": f"https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{BANKING_COMMIT}/banking_data/test.csv",
    "banking_train": f"https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{BANKING_COMMIT}/banking_data/train.csv",
    "anli_test_r3": "https://huggingface.co/datasets/facebook/anli/resolve/refs%2Fconvert%2Fparquet/plain_text/test_r3/0000.parquet",
    "anli_train_r3": "https://huggingface.co/datasets/facebook/anli/resolve/refs%2Fconvert%2Fparquet/plain_text/train_r3/0000.parquet",
    "judgebench_gpt": "https://huggingface.co/datasets/ScalerLab/JudgeBench/resolve/refs%2Fconvert%2Fparquet/default/gpt/0000.parquet",
    "judgebench_claude": "https://huggingface.co/datasets/ScalerLab/JudgeBench/resolve/refs%2Fconvert%2Fparquet/default/claude/0000.parquet",
}
LICENSES = {
    "folio": "CC-BY-SA-4.0 per Yale-LILY/FOLIO LICENSE (verify before redistributing text)",
    "banking77": "CC-BY-4.0",
    "anli": "CC-BY-NC-4.0",
    "judgebench": "MIT (HF card); underlying source questions carry their own licenses",
}
DEV_SEED = 20261010  # sealed before any model call; recorded in development_ids.json

FOLIO_INSTR = (
    "Decide whether the conclusion follows from the premises, using only the premises. "
    "Choose True if the premises entail the conclusion, False if the premises entail its negation, "
    "and Unknown if neither follows."
)
ANLI_INSTR = (
    "Decide the relationship between the premise and the hypothesis. entailment: the hypothesis is "
    "definitely true given the premise; contradiction: the hypothesis is definitely false given the "
    "premise; neutral: neither is determined by the premise."
)
BANKING_INSTR = (
    "A customer sent a message to a bank's support channel. Select the intent category that best "
    "describes the message."
)
JUDGE_INSTR = (
    "Two responses to the same question are shown. Decide which response is better. Correctness is "
    "the primary criterion; you may use relevant knowledge to check the responses."
)
FOLIO_CHOICES = ("True", "False", "Unknown")
ANLI_CHOICES = ("entailment", "neutral", "contradiction")
JUDGE_CHOICES = ("Response A is better", "Response B is better")
BANKING_CANDIDATES = 16


# ---------------------------------------------------------------- download
def fetch(name: str, raw_dir: Path) -> tuple[bytes, dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{name}{Path(SOURCES[name].split('?')[0]).suffix}"
    if not path.exists():
        r = requests.get(SOURCES[name], timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    data = path.read_bytes()
    return data, {"name": name, "url": SOURCES[name], "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _parquet_rows(data: bytes) -> list[dict]:
    import pyarrow.parquet as pq
    return pq.read_table(io.BytesIO(data)).to_pylist()


# ---------------------------------------------------------------- FOLIO
def _folio_label(lbl: str) -> str:
    return {"True": "True", "False": "False", "Uncertain": "Unknown", "Unknown": "Unknown"}[lbl]


def _premise_key(premises) -> str:
    sents = premises if isinstance(premises, list) else [premises]
    return sha256("\n".join(s.strip() for s in sents))[:16]


def _folio_task(row, idx, split, prefix) -> tuple[Task, Gold]:
    prem = row["premises"] if isinstance(row["premises"], list) else [row["premises"]]
    label = _folio_label(row["label"])
    t = Task(
        task_id=f"{prefix}-{idx:04d}", family="folio", split=split,
        cluster_id=f"folio-story-{_premise_key(prem)}",
        instructions=FOLIO_INSTR,
        evidence="Premises:\n" + "\n".join(f"{i+1}. {p.strip()}" for i, p in enumerate(prem)),
        question=f"Conclusion: {row['conclusion'].strip()} Is the conclusion True, False, or Unknown?",
        choices=FOLIO_CHOICES,
    )
    return t, Gold(t.task_id, LETTERS[FOLIO_CHOICES.index(label)], label)


def _jsonl(data: bytes) -> list[dict]:
    return [json.loads(l) for l in data.decode("utf-8").splitlines() if l.strip()]


def load_folio_final(raw: Path):
    data, src = fetch("folio_validation", raw)
    pairs = [_folio_task(r, i, "final", "folio-val") for i, r in enumerate(_jsonl(data))]
    return pairs, [src]


def folio_dev_pool(raw: Path):
    """FOLIO train rows whose stories share no premise sentence with validation."""
    vdata, _ = fetch("folio_validation", raw)
    tdata, src = fetch("folio_train", raw)
    val_sents = {s.strip() for r in _jsonl(vdata) for s in (r["premises"] if isinstance(r["premises"], list) else [r["premises"]])}
    out = []
    for i, r in enumerate(_jsonl(tdata)):
        prem = r["premises"] if isinstance(r["premises"], list) else [r["premises"]]
        if any(p.strip() in val_sents for p in prem):
            continue
        out.append(_folio_task(r, i, "dev", "folio-train"))
    return out, [src]


# ---------------------------------------------------------------- ANLI
def _anli_task(row, split, prefix) -> tuple[Task, Gold]:
    label = ANLI_CHOICES[row["label"]]
    t = Task(
        task_id=f"{prefix}-{row['uid']}", family="anli", split=split,
        cluster_id=f"anli-premise-{sha256(row['premise'].strip())[:16]}",
        instructions=ANLI_INSTR,
        evidence=f"Premise: {row['premise'].strip()}",
        question=f"Hypothesis: {row['hypothesis'].strip()} What is the relationship?",
        choices=ANLI_CHOICES,
    )
    return t, Gold(t.task_id, LETTERS[ANLI_CHOICES.index(label)], label)


def load_anli_final(raw: Path):
    data, src = fetch("anli_test_r3", raw)
    return [_anli_task(r, "final", "anli-test-r3") for r in _parquet_rows(data)], [src]


def anli_dev_pool(raw: Path):
    tdata, _ = fetch("anli_test_r3", raw)
    test_premises = {r["premise"].strip() for r in _parquet_rows(tdata)}
    data, src = fetch("anli_train_r3", raw)
    rows = [r for r in _parquet_rows(data) if r["premise"].strip() not in test_premises and r["label"] in (0, 1, 2)]
    return [_anli_task(r, "dev", "anli-train-r3") for r in rows], [src]


# ---------------------------------------------------------------- Banking77
def humanize(label: str) -> str:
    return label.replace("_", " ")


def _tokens(text: str) -> list[str]:
    w = re.findall(r"[a-z0-9']+", text.lower())
    return w + [a + " " + b for a, b in zip(w, w[1:])]


def banking_confusable_sets(train_rows: list[dict]) -> dict[str, list[str]]:
    """For each label, the 15 labels whose TF-IDF training-utterance centroids are most similar.

    Uses only Banking77 *train* text, never test rows or model outputs, so the
    candidate set is fixed before any call and identical for every model.
    """
    by_label = defaultdict(list)
    for r in train_rows:
        by_label[r["category"]].append(_tokens(r["text"]))
    labels = sorted(by_label)
    df = Counter(t for docs in by_label.values() for d in docs for t in set(d))
    n_docs = sum(len(v) for v in by_label.values())
    vocab = {t: i for i, t in enumerate(sorted(t for t, c in df.items() if c >= 2))}
    import numpy as np
    idf = np.zeros(len(vocab))
    for t, i in vocab.items():
        idf[i] = math.log((1 + n_docs) / (1 + df[t])) + 1
    cent = np.zeros((len(labels), len(vocab)))
    for li, lab in enumerate(labels):
        for d in by_label[lab]:
            v = np.zeros(len(vocab))
            for t in d:
                if t in vocab:
                    v[vocab[t]] += 1
            v *= idf
            nrm = np.linalg.norm(v)
            if nrm:
                cent[li] += v / nrm
        cent[li] /= np.linalg.norm(cent[li]) or 1
    sim = cent @ cent.T
    out = {}
    for li, lab in enumerate(labels):
        order = [labels[j] for j in np.argsort(-sim[li], kind="stable") if j != li]
        out[lab] = order[: BANKING_CANDIDATES - 1]
    return out


def _banking_task(row, idx, split, prefix, confusable) -> tuple[Task, Gold]:
    gold = row["category"]
    cands = [gold] + confusable[gold]
    rng = random.Random(f"{DEV_SEED}-{prefix}-{idx}")  # shared option-order schedule
    rng.shuffle(cands)
    t = Task(
        task_id=f"{prefix}-{idx:04d}", family="banking77", split=split,
        cluster_id=f"banking-{prefix}-{idx:04d}",
        instructions=BANKING_INSTR,
        evidence=f"Customer message: {row['text'].strip()}",
        question="Which intent category best describes the customer message?",
        choices=tuple(humanize(c) for c in cands),
        meta={"candidate_policy": "gold+15 most similar train-centroid labels"},
    )
    return t, Gold(t.task_id, LETTERS[cands.index(gold)], gold)


def _csv(data: bytes) -> list[dict]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


def load_banking_final(raw: Path):
    tr, src_tr = fetch("banking_train", raw)
    te, src_te = fetch("banking_test", raw)
    conf = banking_confusable_sets(_csv(tr))
    return [_banking_task(r, i, "final", "banking-test", conf) for i, r in enumerate(_csv(te))], [src_te, src_tr]


def banking_dev_pool(raw: Path):
    tr, src = fetch("banking_train", raw)
    rows = _csv(tr)
    conf = banking_confusable_sets(rows)
    return [_banking_task(r, i, "dev", "banking-train", conf) for i, r in enumerate(rows)], [src]


# ---------------------------------------------------------------- JudgeBench
def _judge_task(row, split_name) -> tuple[Task, Gold]:
    label = row["label"].strip()
    if label not in ("A>B", "B>A"):
        raise ValueError(f"unexpected JudgeBench label {label!r}")
    t = Task(
        task_id=f"judgebench-{split_name}-{row['pair_id']}", family="judgebench", split=f"final_{split_name}",
        cluster_id=f"judgebench-src-{row['source']}-{row['original_id']}",
        instructions=JUDGE_INSTR,
        evidence=f"Question:\n{row['question'].strip()}\n\nResponse A:\n{row['response_A'].strip()}\n\nResponse B:\n{row['response_B'].strip()}",
        question="Which response is better?",
        choices=JUDGE_CHOICES,
        meta={"source": row["source"]},
    )
    return t, Gold(t.task_id, "A" if label == "A>B" else "B", label)


def load_judgebench_final(raw: Path):
    pairs, srcs = [], []
    for split_name in ("gpt", "claude"):
        data, src = fetch(f"judgebench_{split_name}", raw)
        srcs.append(src)
        pairs += [_judge_task(r, split_name) for r in _parquet_rows(data)]
    return pairs, srcs


# ---------------------------------------------------------------- sampling
def stratified_sample(pairs, n, seed, key=lambda p: p[1].answer_label):
    """Label-stratified, cluster-distinct sample chosen by a sealed seed."""
    rng = random.Random(seed)
    groups = defaultdict(list)
    for p in sorted(pairs, key=lambda p: p[0].task_id):
        groups[key(p)].append(p)
    for g in groups.values():
        rng.shuffle(g)
    labels = sorted(groups)
    out, used_clusters, i = [], set(), 0
    while len(out) < n and any(groups.values()):
        lab = labels[i % len(labels)]
        i += 1
        while groups[lab]:
            p = groups[lab].pop()
            if p[0].cluster_id not in used_clusters:
                used_clusters.add(p[0].cluster_id)
                out.append(p)
                break
    return out


def build_dev_pilot(raw: Path, per_family: int = 6, exclude_ids: frozenset = frozenset(), seed: int = DEV_SEED):
    """The fixed development pool: per_family each of Banking77 train, ANLI train_r3, FOLIO train, judge practice."""
    pools, srcs = {}, []
    for fam, fn in (("banking77", banking_dev_pool), ("anli", anli_dev_pool), ("folio", folio_dev_pool)):
        p, s = fn(raw)
        pools[fam] = [x for x in p if x[0].task_id not in exclude_ids]
        srcs += s
    out = []
    for fam in ("banking77", "anli", "folio"):
        out += stratified_sample(pools[fam], per_family, f"{seed}-{fam}")
    out += judge_practice_tasks()[:per_family]
    return out, srcs


# ---------------------------------------------------------------- ProofWriter bridge (exploratory amendment A2)
SOURCES["proofwriter_test"] = ("https://huggingface.co/datasets/tasksource/proofwriter/resolve/"
                               "refs%2Fconvert%2Fparquet/default/test/0000.parquet")
# Task wording copied verbatim from Hard-Decisions v0.1.0 (MIT), task proofwriter-owa, so JEV-9B's depth curve
# can be set beside the published official-Jev curve. Item samples differ (their IDs are not released).
HD_OWA_INSTR = ("Using only the facts and rules in the text, is the statement true, false, or unknown? A statement is true "
                "if it can be derived from the facts and rules, and false if its negation can be derived. If neither the "
                "statement nor its negation can be derived, it is unknown. A rule applies only when all of its conditions "
                "are established; 'not' in a condition requires the negation to be stated or derived.")
HD_OWA_CHOICES = ("true", "false", "unknown")


def load_proofwriter_bridge(raw: Path, per_cell: int = 50, seed: int = DEV_SEED):
    data, src = fetch("proofwriter_test", raw)
    rows = [r for r in _parquet_rows(data) if "-OWA-" in r["id"] and r["config"] != "NatLang" and 0 <= r["QDep"] <= 5]
    cells = defaultdict(list)
    for i, r in enumerate(rows):
        cells[(int(r["QDep"]), r["answer"].lower())].append((i, r))
    pairs = []
    for (dep, lab) in sorted(cells):
        pool = cells[(dep, lab)]
        rng = random.Random(f"{seed}-pw-{dep}-{lab}")
        for i, r in sorted(rng.sample(pool, min(per_cell, len(pool))), key=lambda x: x[0]):
            t = Task(
                task_id=f"pw-{r['id']}-{i}", family="proofwriter", split="bridge",
                cluster_id=f"pw-theory-{r['id']}",
                instructions=HD_OWA_INSTR, evidence=r["theory"].strip(),
                question=f"Statement: {r['question'].strip()}", choices=HD_OWA_CHOICES,
                meta={"depth": dep, "config": r["config"], "n_rules": r["NRule"], "n_facts": r["NFact"]},
            )
            pairs.append((t, Gold(t.task_id, LETTERS[HD_OWA_CHOICES.index(lab)], lab)))
    return pairs, [src]
