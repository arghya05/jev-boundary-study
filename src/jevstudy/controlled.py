"""Controlled dependency panel (G01; optional G02).

Formal fragment
---------------
* Unary predicates over named entities; signed ground facts; universally
  quantified single-premise rules `L1(x) -> L2(x)` whose body and head are
  signed literals. Classical semantics; open-world True/False/Unknown answers.
* True: the target literal is classically entailed. False: its negation is.
  Unknown: neither. Inconsistent worlds are rejected before any model call.

Item construction (one *base seed* -> six depth/context conditions)
* A derivation chain l0 -> l1 -> ... -> ld ends at the target predicate.
* The total rule count is fixed (`N_RULES`); 8-d unused rules form short
  distractor chains from never-satisfied predicates, one ending at the target
  predicate with the opposite sign, so surface rule structure does not reveal d.
* Each item has exactly two facts about the target entity (start fact + decoy);
  the `irrelevant` context condition adds 8 facts about other entities.
* Label: True/False by the sign of the final chain head; Unknown by stating the
  start fact with the opposite sign (nothing fires). The label is fixed per seed.

Two independent reference scorers must agree: brute-force classical
entailment over truth assignments, and forward chaining with derivation depth.
Every rendered sentence is parsed back to its formula (fidelity round trip).
"""
from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass

import numpy as np

from .canonical import LETTERS, Gold, Task

ADJECTIVES = (
    "dravic florin gremal hustic jorvan kelpid lumbic morvex narlin pexton quorin rustal sombic tarvin "
    "vexlan wumpic yorbin zelvic bontic cravel delmor fenric gostal hobrin jaskel kombar lintor mavric "
    "nostel parvin ribrel solvar tembic ulvarn vintor welbic xantic yelmar zorvin brelic"
).split()
NAMES = "Avery Blake Casey Devon Ellis Finch Grant Hayes Jesse Kerry Logan Mason Noble Owens Perry Quinn Reese Sasha Tatum Wynne".split()
N_RULES = 8
N_IRRELEVANT = 8
DEPTHS = (1, 3, 5)
CONTEXTS = (0, N_IRRELEVANT)
LABELS = ("True", "False", "Unknown")
CHOICES = ("True", "False", "Unknown")
INSTR = (
    "Decide whether the statement follows from the facts and rules, using only the facts and rules. "
    "Choose True if they entail the statement, False if they entail its negation, and Unknown if neither follows."
)

Lit = tuple  # (predicate, positive: bool)


@dataclass
class World:
    target_entity: str
    facts: list          # [(entity, (pred, pos))]
    rules: list          # [((pred, pos), (pred, pos))]
    target: Lit          # (pred, True) - the statement asked about is always positive
    order: list          # premise rendering order: list of ("f", i) / ("r", i)


# ---------------------------------------------------------------- templates
TEMPLATES = {
    "T1": {
        "fact": ("{e} is {a}.", "{e} is not {a}."),
        "rule": "If someone is {b}, then they are {h}.",
        "neg": "not {a}",
    },
    "T2": {
        "fact": ("It is known that {e} is {a}.", "It is known that {e} is not {a}."),
        "rule": "Everyone who is {b} is also {h}.",
        "neg": "not {a}",
    },
}


def _lit_text(lit, tpl):
    p, pos = lit
    return p if pos else TEMPLATES[tpl]["neg"].format(a=p)


def render_fact(ent, lit, tpl):
    return TEMPLATES[tpl]["fact"][0 if lit[1] else 1].format(e=ent, a=lit[0])


def render_rule(rule, tpl):
    b, h = rule
    return TEMPLATES[tpl]["rule"].format(b=_lit_text(b, tpl), h=_lit_text(h, tpl))


def render_world(w: World, tpl: str) -> list[str]:
    out = []
    for kind, i in w.order:
        out.append(render_fact(*w.facts[i], tpl) if kind == "f" else render_rule(w.rules[i], tpl))
    return out


def parse_sentence(s: str, tpl: str):
    """Inverse of the renderers; used for the automated fidelity round trip."""
    lit = r"(not )?([a-z]+)"
    if tpl == "T1":
        m = re.fullmatch(rf"If someone is {lit}, then they are {lit}\.", s)
        if m:
            return ("r", ((m[2], m[1] is None), (m[4], m[3] is None)))
        m = re.fullmatch(rf"([A-Z][a-z]+) is {lit}\.", s)
        if m:
            return ("f", (m[1], (m[3], m[2] is None)))
    else:
        m = re.fullmatch(rf"Everyone who is {lit} is also {lit}\.", s)
        if m:
            return ("r", ((m[2], m[1] is None), (m[4], m[3] is None)))
        m = re.fullmatch(rf"It is known that ([A-Z][a-z]+) is {lit}\.", s)
        if m:
            return ("f", (m[1], (m[3], m[2] is None)))
    raise ValueError(f"unparseable sentence: {s!r}")


# ---------------------------------------------------------------- reference scorers
def entails_bruteforce(facts_e: list, rules: list, query: Lit) -> str:
    """Classical entailment for one entity by enumerating truth assignments.

    Rules are universally quantified unary implications, so the grounding for
    one entity is independent of other entities' facts.
    """
    preds = sorted({p for p, _ in facts_e} | {p for r in rules for p, _ in r} | {query[0]})
    idx = {p: i for i, p in enumerate(preds)}
    n = len(preds)
    if n > 22:
        raise ValueError("too many atoms for brute force")
    a = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(bool)
    ok = np.ones(len(a), dtype=bool)
    for p, pos in facts_e:
        ok &= a[:, idx[p]] == pos
    for (bp, bpos), (hp, hpos) in rules:
        ok &= ~(a[:, idx[bp]] == bpos) | (a[:, idx[hp]] == hpos)
    if not ok.any():
        return "INCONSISTENT"
    models = a[ok]
    q = models[:, idx[query[0]]]
    if (q == query[1]).all():
        return "True"
    if (q != query[1]).all():
        return "False"
    return "Unknown"


def forward_chain(facts_e: list, rules: list, query: Lit) -> tuple[str, int | None]:
    """Independent second scorer: modus-ponens closure with derivation depth."""
    depth = {lit: 0 for lit in facts_e}
    changed = True
    while changed:
        changed = False
        for b, h in rules:
            if b in depth and (h not in depth or depth[h] > depth[b] + 1):
                depth[h] = depth[b] + 1
                changed = True
    neg = (query[0], not query[1])
    if query in depth and neg in depth:
        return "INCONSISTENT", None
    if query in depth:
        return "True", depth[query]
    if neg in depth:
        return "False", depth[neg]
    return "Unknown", None


def facts_of(w: World, ent: str) -> list:
    return [lit for e, lit in w.facts if e == ent]


def reference_label(w: World) -> dict:
    """Both scorers on the target entity; every entity's grounding must be consistent."""
    for ent in {e for e, _ in w.facts}:
        if entails_bruteforce(facts_of(w, ent), w.rules, (ADJECTIVES[0], True)) == "INCONSISTENT":
            return {"label": "INCONSISTENT"}
    fe = facts_of(w, w.target_entity)
    bf = entails_bruteforce(fe, w.rules, w.target)
    fc, d = forward_chain(fe, w.rules, w.target)
    return {"label": bf if bf == fc else "DISAGREE", "bruteforce": bf, "forward": fc, "derivation_depth": d}


# ---------------------------------------------------------------- generator
def _gen_base(seed: int, label: str):
    """Sample everything shared by a seed's six conditions."""
    rng = random.Random(seed)
    adjs = rng.sample(ADJECTIVES, len(ADJECTIVES))
    names = rng.sample(NAMES, len(NAMES))
    return rng, adjs, names


def build_world(seed: int, label: str, depth: int, n_irrelevant: int) -> World:
    """Deterministic: the same (seed, label) shares entities and vocabulary across conditions."""
    rng, adjs, names = _gen_base(seed, label)
    target_e, others = names[0], names[1:1 + N_IRRELEVANT]
    pool = iter(adjs)
    target_pred = next(pool)
    chain_preds = [next(pool) for _ in range(depth)] + [target_pred]  # l0..ld
    chain_signs = [rng.random() < 0.5 for _ in range(depth)] + [label != "False"]
    chain = list(zip(chain_preds, chain_signs))
    rules = [(chain[i], chain[i + 1]) for i in range(depth)]
    # distractor chains from never-satisfied predicates, lengths 1-2; the first ends at the target with opposite sign
    remaining = N_RULES - depth
    first = True
    while remaining > 0:
        L = 1 if remaining == 1 else rng.choice((1, 2))
        preds = [next(pool) for _ in range(L)]
        heads = preds[1:] + [None]
        if first:
            end = (target_pred, label == "False")
            first = False
        else:
            end = (next(pool), rng.random() < 0.5)
        lits = [(p, rng.random() < 0.5) for p in preds] + [end]
        rules += [(lits[i], lits[i + 1]) for i in range(L)]
        remaining -= L
    start = chain[0] if label != "Unknown" else (chain[0][0], not chain[0][1])
    decoy = (next(pool), rng.random() < 0.5)
    facts = [(target_e, start), (target_e, decoy)]
    vocab = [p for r in rules for p, _ in r]
    for e in others[:n_irrelevant]:
        facts.append((e, (rng.choice(vocab), rng.random() < 0.5)))
    order = [("f", i) for i in range(len(facts))] + [("r", i) for i in range(len(rules))]
    rng.shuffle(order)
    return World(target_e, facts, rules, (target_pred, True), order)


def make_task(w: World, tpl: str, task_id: str, split: str, cluster: str, meta: dict) -> tuple[Task, Gold]:
    ref = reference_label(w)
    if ref["label"] not in LABELS:
        raise ValueError(f"{task_id}: reference failure {ref}")
    sents = render_world(w, tpl)
    # fidelity round trip: parse every sentence back and compare with the formal world
    parsed = [parse_sentence(s, tpl) for s in sents]
    expected = [("f", w.facts[i]) if k == "f" else ("r", w.rules[i]) for k, i in w.order]
    if parsed != expected:
        raise ValueError(f"{task_id}: rendering does not round-trip")
    t = Task(
        task_id=task_id, family="controlled", split=split, cluster_id=cluster,
        instructions=INSTR,
        evidence="Facts and rules:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(sents)),
        question=f"Statement: {w.target_entity} is {w.target[0]}. Is the statement True, False, or Unknown?",
        choices=CHOICES,
        meta={**meta, "derivation_depth": ref["derivation_depth"], "n_sentences": len(sents)},
    )
    return t, Gold(task_id, LETTERS[CHOICES.index(ref["label"])], ref["label"])


def panel(seeds: list[int], split: str, templates: dict[int, str], controls: bool = True,
          evidence_removal: bool = False, control_cell=(3, N_IRRELEVANT)):
    """All depth x context conditions per seed, plus paired controls at `control_cell`."""
    out = []
    for k, seed in enumerate(seeds):
        label = LABELS[k % 3]
        tpl = templates[seed]
        cluster = f"graph-{seed}"
        for depth, ctx in itertools.product(DEPTHS, CONTEXTS):
            w = build_world(seed, label, depth, ctx)
            meta = {"seed": seed, "depth": depth, "irrelevant": ctx, "template": tpl, "condition": "base", "base_label": label}
            out.append(make_task(w, tpl, f"ctl-{seed}-d{depth}-c{ctx}", split, cluster, meta))
        if controls:
            depth, ctx = control_cell
            w = build_world(seed, label, depth, ctx)
            # decision-changing: flip the final chain head (True<->False) or, for Unknown, flip the start fact
            if label == "Unknown":
                wc = World(w.target_entity, [(w.target_entity, (w.facts[0][1][0], not w.facts[0][1][1]))] + w.facts[1:],
                           w.rules, w.target, w.order)
            else:
                rules = list(w.rules)
                b, (hp, hpos) = rules[depth - 1]
                rules[depth - 1] = (b, (hp, not hpos))
                wc = World(w.target_entity, w.facts, rules, w.target, w.order)
            meta = {"seed": seed, "depth": depth, "irrelevant": ctx, "template": tpl, "condition": "decision_changing", "base_label": label}
            out.append(make_task(wc, tpl, f"ctl-{seed}-change", split, cluster, meta))
            # decision-preserving: rename every entity and reorder premises
            rng = random.Random(f"preserve-{seed}")
            ents = sorted({e for e, _ in w.facts})
            fresh = rng.sample([n for n in NAMES if n not in ents], len(ents))
            ren = dict(zip(ents, fresh))
            order = list(w.order)
            rng.shuffle(order)
            wp = World(ren[w.target_entity], [(ren[e], l) for e, l in w.facts], w.rules, w.target, order)
            meta = {**meta, "condition": "decision_preserving"}
            out.append(make_task(wp, tpl, f"ctl-{seed}-preserve", split, cluster, meta))
        if evidence_removal:
            # G02: drop the start fact, replaced by a length-matched fact about an uninvolved entity
            depth, ctx = control_cell
            w = build_world(seed, label, depth, ctx)
            if label != "Unknown":
                spare = next(n for n in NAMES if n not in {e for e, _ in w.facts})
                facts = [(spare, w.facts[0][1])] + w.facts[1:]
                wr = World(w.target_entity, facts, w.rules, w.target, w.order)
                meta = {"seed": seed, "depth": depth, "irrelevant": ctx, "template": tpl, "condition": "evidence_removed", "base_label": label}
                out.append(make_task(wr, tpl, f"ctl-{seed}-removed", split, cluster, meta))
    return out


DEV_SEEDS = list(range(9001, 9007))                  # 6 development seeds (2 per label), template T1
FINAL_SEEDS = list(range(424242, 424242 + 48))       # 48 sealed held-out seeds


def dev_panel():
    return panel(DEV_SEEDS, "controlled_dev", {s: "T1" for s in DEV_SEEDS})


def final_panel(evidence_removal: bool = False):
    # half the held-out seeds use the unseen template T2 (transfer check for the selection rule)
    tpl = {s: ("T1" if i % 2 == 0 else "T2") for i, s in enumerate(FINAL_SEEDS)}
    return panel(FINAL_SEEDS, "controlled_final", tpl, evidence_removal=evidence_removal)
