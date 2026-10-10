"""jev-judge: cheap, calibrated LLM evaluation with JEV-9B (alias of the `jevstudy` package).

    from jevjudge import JevClient, Router
"""
from jevstudy.toolkit import JevClient, Router  # noqa: F401
from jevstudy import evaluate  # noqa: F401

__all__ = ["JevClient", "Router", "evaluate"]
