"""Canonical task objects.

One `Task` carries everything any model may see. Gold labels live in a separate
`Gold` record keyed by task_id and are never attached to a Task, so an adapter
cannot leak them. Every model receives the same instructions, evidence, question,
choices and choice order; only the transport wrapper differs.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

PROTOCOL_VERSION = "jevstudy-protocol-1"
LETTERS = "ABCDEFGHIJKLMNOP"  # JEV-9B's choice head supports at most 16 options
FINAL_INSTRUCTION = (
    "Select the correct choice using the supplied information and task definition. "
    "Return the final choice identifier."
)


@dataclass(frozen=True)
class Task:
    task_id: str
    family: str          # folio | anli | banking77 | judgebench | controlled | judge_practice
    split: str           # dev | final | controlled_dev | controlled_final ...
    cluster_id: str      # independent sampling unit (story, source question, graph seed)
    instructions: str
    evidence: str
    question: str
    choices: tuple[str, ...]
    meta: dict = field(default_factory=dict, compare=False, hash=False)  # model-independent annotations only

    def __post_init__(self):
        if not 2 <= len(self.choices) <= len(LETTERS):
            raise ValueError(f"{self.task_id}: {len(self.choices)} choices; supported range is 2-16")
        if len(set(self.choices)) != len(self.choices):
            raise ValueError(f"{self.task_id}: duplicate choices")

    @property
    def choice_ids(self) -> tuple[str, ...]:
        return tuple(LETTERS[: len(self.choices)])

    def to_json(self) -> dict:
        d = asdict(self)
        d["choices"] = list(self.choices)
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Task":
        d = dict(d)
        d["choices"] = tuple(d["choices"])
        return cls(**d)


@dataclass(frozen=True)
class Gold:
    task_id: str
    answer_id: str       # letter of the correct choice
    answer_label: str    # dataset label, e.g. "True", "entailment", "card_arrival", "A>B"


def choice_lines(task: Task) -> list[str]:
    return [f"{cid}) {text}" for cid, text in zip(task.choice_ids, task.choices)]


def render(task: Task) -> str:
    """The canonical task text sent (verbatim) to the frontier models."""
    return (
        f"Task: {task.instructions}\n\n"
        f"Evidence:\n{task.evidence}\n\n"
        f"Question: {task.question}\n\n"
        "Choices:\n" + "\n".join(choice_lines(task)) + "\n\n" + FINAL_INSTRUCTION
    )


def jev_state(task: Task) -> str:
    """The [state] field of JEV-9B's typed template: same instructions and evidence."""
    return f"Task: {task.instructions}\n\nEvidence:\n{task.evidence}"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def task_hash(task: Task) -> str:
    """Hash of the semantic content all models receive (not of meta)."""
    payload = {
        "protocol": PROTOCOL_VERSION,
        "instructions": task.instructions,
        "evidence": task.evidence,
        "question": task.question,
        "choices": list(task.choices),
    }
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def write_jsonl(path, rows) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
