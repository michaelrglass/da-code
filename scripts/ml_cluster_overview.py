#!/usr/bin/env python3
"""Generate a markdown overview of all ml-cluster tasks."""

import json
import os
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).absolute().parent.parent
TASK_CONFIG = REPO_ROOT / "da_code" / "configs" / "task" / "ml.jsonl"
EVAL_CONFIG = REPO_ROOT / "da_code" / "configs" / "eval" / "eval_ml.jsonl"
GOLD_DIR = REPO_ROOT / "da_code" / "gold"
SOURCE_DIR = REPO_ROOT / "da_code" / "source"
OUTPUT = REPO_ROOT / "scripts" / "ml_cluster_overview.md"


def load_jsonl(path, prefix="ml-cluster"):
    items = {}
    with open(path) as f:
        for line in f:
            obj = json.loads(line)
            if obj["id"].startswith(prefix):
                items[obj["id"]] = obj
    return items


def head_lines(path, n=20):
    """Read first n lines of a file, return as string."""
    lines = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line.rstrip())
    except Exception as e:
        lines.append(f"(error reading file: {e})")
    return "\n".join(lines)


def main():
    tasks = load_jsonl(TASK_CONFIG)
    evals = load_jsonl(EVAL_CONFIG)

    task_ids = sorted(tasks.keys())

    parts = ["# ML Cluster Tasks Overview\n"]

    for tid in task_ids:
        task = tasks[tid]
        ev = evals.get(tid, {})

        parts.append(f"---\n## {tid}\n")

        # Task metadata
        parts.append(f"**Hardness**: {task.get('hardness', '?')}\n")
        parts.append(f"**Instruction**:\n> {task['instruction']}\n")

        # Eval config
        config = ev.get("config", {})
        options = ev.get("options", [{}])
        result_files = ev.get("result", [])
        parts.append("**Eval Config**:\n")
        parts.append(f"- Metric: `{config.get('metric', '?')}`")
        parts.append(f"- Upper bound: `{config.get('upper_bound', '?')}`")
        parts.append(f"- Lower bound: `{config.get('lower_bound', '?')}`")
        parts.append(f"- Result file(s): {[r.get('file','?') for r in result_files]}")
        parts.append(f"- Options: `{options}`\n")

        # Gold file
        gold_dir = GOLD_DIR / tid
        if gold_dir.exists():
            for gf in sorted(gold_dir.iterdir()):
                if gf.suffix == ".csv":
                    parts.append(f"**Gold file**: `{gf.name}`\n")
                    parts.append("```csv")
                    parts.append(head_lines(gf, 20))
                    parts.append("```\n")

        # Source files
        source_dir = SOURCE_DIR / tid
        if source_dir.exists():
            parts.append("**Source files**:\n")
            for sf in sorted(source_dir.iterdir()):
                size_kb = sf.stat().st_size / 1024
                if sf.suffix in (".csv", ".md", ".txt", ".json"):
                    parts.append(f"### `{sf.name}` ({size_kb:.1f} KB)\n")
                    parts.append("```")
                    parts.append(head_lines(sf, 20))
                    parts.append("```\n")
                else:
                    parts.append(f"### `{sf.name}` ({size_kb:.1f} KB) *(binary/non-text, preview skipped)*\n")

        parts.append("")

    output_text = "\n".join(parts)
    OUTPUT.write_text(output_text)
    print(f"Written to {OUTPUT}")


if __name__ == "__main__":
    main()
