"""Shared adapter types. Adapters never see Gold."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field

from ..canonical import PROTOCOL_VERSION, Task, sha256, task_hash

ANSWER_SCHEMA_NAME = "decision"


def answer_schema(task: Task) -> dict:
    return {
        "type": "object",
        "properties": {"answer": {"type": "string", "enum": list(task.choice_ids)}},
        "required": ["answer"],
        "additionalProperties": False,
    }


@dataclass
class Result:
    system: str                 # configuration key, e.g. "astra-high"
    task_id: str
    task_hash: str
    request_key: str
    status: str                 # ok | invalid | refusal | truncated | error
    answer_id: str | None
    distribution: dict | None = None   # JEV-9B System 1 calibrated probabilities over choice ids
    usage: dict = field(default_factory=dict)
    cost_usd: float = 0.0
    latency_s: float | None = None
    resolved_model: str | None = None
    attempts: int = 1
    mode: str = "sync"          # sync | batch | local
    error: str | None = None
    raw: dict | None = None     # sanitized provider response metadata
    created_at: float = field(default_factory=time.time)

    def to_json(self) -> dict:
        return asdict(self)


class Adapter:
    system: str
    config: dict

    def request_key(self, task: Task) -> str:
        """Cache key: exact task content + model + version + effort + schema + protocol."""
        return sha256(json.dumps({"task": task_hash(task), "system": self.system, "config": self.config,
                                  "protocol": PROTOCOL_VERSION}, sort_keys=True))

    def max_cost(self, task: Task) -> float:
        return 0.0

    def run(self, task: Task) -> Result:  # pragma: no cover - interface
        raise NotImplementedError


TRANSIENT_HTTP = {408, 409, 429, 500, 502, 503, 504, 520, 529}


def est_tokens(text: str) -> int:
    """Conservative pre-call estimate (~3 chars/token) used only for reservations."""
    return int(len(text) / 3) + 64
