#!/usr/bin/env python3
"""PreToolUse guard for Bash commands.

Deterministic enforcement of two iron laws:
  1. Destructive ops get a confirmation (ml-careful, always-on).
  2. Training launches require a logged hypothesis (journal-first).

Reads the hook payload from stdin, emits a JSON decision on stdout.
Default: approve silently. Fail-open on any internal error — a broken
guard must never block normal work.
"""
import json
import os
import re
import sys


def out(decision, reason=None):
    payload = {"decision": decision}
    if reason:
        payload["reason"] = reason
    print(json.dumps(payload))
    sys.exit(0)


DESTRUCTIVE = [
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\b.*\b(ml|experiments|checkpoints?|models?|data)\b",
     "recursive force-delete touching ML state/artifact paths"),
    (r"\baws\s+s3\s+(rm\b.*--recursive|sync\b.*--delete)",
     "S3 recursive delete / destructive sync"),
    (r"\b(drop\s+table|truncate\s+table|truncate\s+\w)", "DROP/TRUNCATE on a table"),
    (r"\bdelete\s+from\s+\w+\s*(;|$)", "DELETE without WHERE clause"),
    (r"\bgit\s+push\b.*(--force(?!-with-lease)\b|\s-f\b)", "force-push (without lease)"),
    (r"\bgit\s+reset\s+--hard", "git reset --hard"),
    (r"\bgit\s+branch\s+-D\b", "force branch deletion"),
    (r"\bmlflow\s+.*\bdelete\b|\bsagemaker\b.*delete-model", "model registry deletion"),
]

TRAINING = re.compile(
    r"\b(torchrun|deepspeed|accelerate\s+launch|sbatch\b.*train|python3?\s+\S*train\S*\.py)\b",
    re.IGNORECASE,
)


def journal_has_open_hypothesis():
    path = "experiments/journal.md"
    if not os.path.exists(path):
        return False
    try:
        return "Status**: PLANNED" in open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        out("approve")
    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command", "") or ""
    if not cmd:
        out("approve")

    low = cmd.lower()
    for pattern, label in DESTRUCTIVE:
        if re.search(pattern, low):
            out("ask_user",
                f"[mlforge guard] Destructive operation detected: {label}. "
                f"Confirm blast radius before running. Command: {cmd[:200]}")

    if TRAINING.search(cmd) and "--dry-run" not in low and not journal_has_open_hypothesis():
        out("ask_user",
            "[mlforge guard] Training launch with no PLANNED hypothesis in "
            "experiments/journal.md. Iron law: log the hypothesis first "
            "(ml-experiment-journal) — or confirm to proceed anyway.")

    out("approve")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        out("approve")
