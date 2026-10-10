"""Six independently authored correctness-judging practice cases (development only).

Written for this study, outside JudgeBench, with objectively checkable answers.
Exactly one response in each pair is correct; three pairs favour A and three favour B.
"""
from __future__ import annotations

from .canonical import Gold, Task

_INSTR = (
    "Two responses to the same question are shown. Decide which response is better. Correctness is "
    "the primary criterion; you may use relevant knowledge to check the responses."
)
_CHOICES = ("Response A is better", "Response B is better")

CASES = [
    ("What is the sum of all positive divisors of 36?",
     "The divisors are 1, 2, 3, 4, 6, 9, 12, 18 and 36. Their sum is 91.",
     "The divisors are 1, 2, 3, 4, 6, 9, 12, 18 and 36. Their sum is 87.",
     "A"),
    ("Write a Python function that returns True when a string is a palindrome, ignoring letter case.",
     "def is_pal(s):\n    return s == s[::-1]",
     "def is_pal(s):\n    t = s.lower()\n    return t == t[::-1]",
     "B"),
    ("Two fair six-sided dice are rolled. What is the probability that the sum is 8?",
     "The pairs (2,6), (3,5), (4,4), (5,3) and (6,2) give 8, so the probability is 5/36.",
     "Each sum from 2 to 12 is roughly equally likely around the middle, so the probability is 1/6.",
     "A"),
    ("How many times is the digit 1 written when writing every integer from 1 to 20?",
     "It appears in 1, 10, 11, 12, 13, 14, 15, 16, 17, 18 and 19, so 11 times.",
     "It appears once each in 1, 10 and 12-19 (10 times) and twice in 11, so 12 times.",
     "B"),
    ("All bloops are razzies. Some razzies are lazzies. Does it follow that some bloops are lazzies?",
     "Yes. Bloops are razzies and some razzies are lazzies, so some bloops must be lazzies.",
     "No. The razzies that are lazzies could all be non-bloops, so the conclusion does not follow.",
     "B"),
    ("How many seconds are there in 3.5 hours?",
     "3.5 hours x 3,600 seconds per hour = 12,600 seconds.",
     "3.5 hours x 6,000 seconds per hour = 21,000 seconds.",
     "A"),
]


def judge_practice_tasks() -> list[tuple[Task, Gold]]:
    out = []
    for i, (q, a, b, better) in enumerate(CASES):
        t = Task(
            task_id=f"judge-practice-{i:02d}", family="judge_practice", split="dev",
            cluster_id=f"judge-practice-{i:02d}",
            instructions=_INSTR,
            evidence=f"Question:\n{q}\n\nResponse A:\n{a}\n\nResponse B:\n{b}",
            question="Which response is better?",
            choices=_CHOICES,
        )
        out.append((t, Gold(t.task_id, better, f"{better}>{'B' if better == 'A' else 'A'}")))
    return out
